"""
Servicio de Pedido.

Orquesta la creación de un pedido completo:
  1. Valida que el cliente exista.
  2. Calcula los campos derivados de cada DetallePedido (via calculadora).
  3. Persiste el Pedido y sus Detalles en una única transacción.
  4. Calcula y guarda los totales del pedido.
"""

import uuid
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.cliente import Cliente
from app.models.pedido import EstadoPedido, Pedido
from app.models.detalle_pedido import DetallePedido
from app.schemas.pedido import PedidoCreate, PedidoUpdate
from app.services.calculadora import calcular_detalle, calcular_totales_pedido


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

def _get_or_404(db: Session, pedido_id: UUID) -> Pedido:
    """Devuelve el pedido con sus detalles cargados (eager) o lanza 404."""
    pedido = (
        db.query(Pedido)
        .options(joinedload(Pedido.detalles))
        .filter(Pedido.id == pedido_id)
        .first()
    )
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido con id={pedido_id} no encontrado.",
        )
    return pedido


def _validar_cliente(db: Session, cliente_id: UUID) -> Cliente:
    """Lanza 404 si el cliente no existe."""
    cliente = db.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente con id={cliente_id} no encontrado.",
        )
    return cliente


# ---------------------------------------------------------------------------
# CRUD público
# ---------------------------------------------------------------------------

def crear_pedido(db: Session, datos: PedidoCreate) -> Pedido:
    """
    Crea un pedido completo con sus detalles en una sola transacción.

    Flujo:
      1. Valida que el cliente exista.
      2. Genera el UUID del pedido manualmente para asignarlo antes del flush.
      3. Por cada DetallePedidoCreate → calcula tax, comisión, precio final, subtotal.
      4. Calcula subtotal_usd, total_usd y total_clp del pedido.
      5. Un único db.flush() al final persiste todo.
      6. Re-query con joinedload para devolver el objeto completo.
    """
    _validar_cliente(db, datos.cliente_id)

    # Generar UUID explícitamente para poder asignarlo a los detalles
    # antes del flush (evita el primer flush intermedio)
    pedido_id = uuid.uuid4()

    # --- Calcular detalles ---
    detalles_orm = []
    subtotales = []

    for item in datos.detalles:
        resultado = calcular_detalle(
            precio_base_usd=item.precio_base_usd,
            porcentaje_tax=item.porcentaje_tax,
            porcentaje_comision=item.porcentaje_comision,
            cantidad=item.cantidad,
        )
        detalle = DetallePedido(
            pedido_id=pedido_id,
            nombre_producto=item.nombre_producto,
            cantidad=item.cantidad,
            precio_base_usd=item.precio_base_usd,
            porcentaje_tax=item.porcentaje_tax,
            porcentaje_comision=item.porcentaje_comision,
            tax_usd=resultado.tax_usd,
            comision_usd=resultado.comision_usd,
            precio_final_usd=resultado.precio_final_usd,
            subtotal_usd=resultado.subtotal_usd,
        )
        detalles_orm.append(detalle)
        subtotales.append(resultado.subtotal_usd)

    # --- Calcular totales del pedido ---
    subtotal_usd, total_usd, total_clp = calcular_totales_pedido(
        subtotales_usd=subtotales,
        valor_dolar=datos.valor_dolar,
    )

    # --- Crear el pedido con todos los campos, incluido el ID explícito ---
    pedido = Pedido(
        id=pedido_id,
        cliente_id=datos.cliente_id,
        estado=EstadoPedido.PENDIENTE,
        valor_dolar=datos.valor_dolar,
        subtotal_usd=subtotal_usd,
        total_usd=total_usd,
        total_clp=total_clp,
    )

    # --- Un único flush para todo ---
    db.add(pedido)
    for detalle in detalles_orm:
        db.add(detalle)

    db.flush()

    # Re-query con joinedload para que los detalles estén cargados
    return _get_or_404(db, pedido_id)


def obtener_pedido(db: Session, pedido_id: UUID) -> Pedido:
    """Devuelve un pedido con sus detalles cargados o lanza 404."""
    return _get_or_404(db, pedido_id)


def listar_pedidos(
    db: Session,
    cliente_id: UUID | None = None,
    estado: EstadoPedido | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Pedido]:
    """
    Listado de pedidos con filtros opcionales.
    """
    limit = min(limit, 200)
    query = db.query(Pedido).order_by(Pedido.created_at.desc())

    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)
    if estado:
        query = query.filter(Pedido.estado == estado)

    return query.offset(skip).limit(limit).all()


def actualizar_estado_pedido(
    db: Session,
    pedido_id: UUID,
    datos: PedidoUpdate,
) -> Pedido:
    """
    Actualiza SOLO el estado del pedido.

    Regla de negocio: el estado solo puede avanzar en la secuencia
        pendiente → en_bodega → enviado
    """
    pedido = _get_or_404(db, pedido_id)

    _orden = {
        EstadoPedido.PENDIENTE: 0,
        EstadoPedido.EN_BODEGA: 1,
        EstadoPedido.ENVIADO: 2,
    }

    if _orden[datos.estado] < _orden[pedido.estado]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"No se puede retroceder el estado de "
                f"'{pedido.estado.value}' a '{datos.estado.value}'."
            ),
        )

    pedido.estado = datos.estado
    db.flush()
    return _get_or_404(db, pedido_id)


def eliminar_pedido(db: Session, pedido_id: UUID) -> None:
    """
    Elimina un pedido y sus detalles (CASCADE en BD).

    Solo se permite eliminar pedidos en estado PENDIENTE.
    """
    pedido = _get_or_404(db, pedido_id)

    if pedido.estado != EstadoPedido.PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Solo se pueden eliminar pedidos en estado 'pendiente'. "
                f"El pedido id={pedido_id} está en estado '{pedido.estado.value}'."
            ),
        )

    db.delete(pedido)
    db.flush()
