"""
Servicio de Cliente.

Contiene toda la lógica de acceso a datos para el modelo Cliente.
Los endpoints importan estas funciones en lugar de hablar directamente
con la sesión, manteniendo los routers delgados y testables.
"""

from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.cliente import Cliente
from app.schemas.cliente import ClienteCreate, ClienteUpdate


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

def _get_or_404(db: Session, cliente_id: UUID) -> Cliente:
    """Devuelve el cliente o lanza 404 si no existe."""
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

def crear_cliente(db: Session, datos: ClienteCreate) -> Cliente:
    """
    Registra un nuevo cliente en la base de datos.

    Valida que el email no esté duplicado si viene informado.
    """
    if datos.email:
        existente = (
            db.query(Cliente)
            .filter(Cliente.email == datos.email)
            .first()
        )
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un cliente con el email '{datos.email}'.",
            )

    cliente = Cliente(
        nombre=datos.nombre,
        telefono=datos.telefono,
        email=datos.email,
    )
    db.add(cliente)
    db.flush()   # obtiene el UUID generado sin hacer commit aún
    return cliente


def obtener_cliente(db: Session, cliente_id: UUID) -> Cliente:
    """Devuelve un cliente por su UUID o lanza 404."""
    return _get_or_404(db, cliente_id)


def listar_clientes(
    db: Session,
    skip: int = 0,
    limit: int = 50,
) -> list[Cliente]:
    """
    Devuelve una página de clientes ordenados por nombre.

    Args:
        skip:  número de registros a omitir (offset).
        limit: máximo de registros a devolver (máx. 200).
    """
    limit = min(limit, 200)
    return (
        db.query(Cliente)
        .order_by(Cliente.nombre)
        .offset(skip)
        .limit(limit)
        .all()
    )


def actualizar_cliente(
    db: Session,
    cliente_id: UUID,
    datos: ClienteUpdate,
) -> Cliente:
    """
    Actualización parcial (PATCH) de un cliente.

    Solo modifica los campos que vienen en el payload (no-None).
    """
    cliente = _get_or_404(db, cliente_id)

    # Validar email único si se está cambiando
    if datos.email and datos.email != cliente.email:
        existente = (
            db.query(Cliente)
            .filter(Cliente.email == datos.email)
            .first()
        )
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un cliente con el email '{datos.email}'.",
            )

    cambios = datos.model_dump(exclude_unset=True)
    for campo, valor in cambios.items():
        setattr(cliente, campo, valor)

    db.flush()
    return cliente


def eliminar_cliente(db: Session, cliente_id: UUID) -> None:
    """
    Elimina un cliente.

    Lanza 409 si el cliente tiene pedidos asociados
    (la FK en Pedido tiene ondelete=RESTRICT a nivel de BD;
    aquí lo validamos antes para devolver un mensaje claro).
    """
    cliente = _get_or_404(db, cliente_id)

    if cliente.pedidos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"No se puede eliminar el cliente id={cliente_id} "
                f"porque tiene {len(cliente.pedidos)} pedido(s) asociado(s)."
            ),
        )

    db.delete(cliente)
    db.flush()
