"""
Router de Pedidos.

Endpoints:
  POST   /pedidos/            → crear pedido completo (con detalles)
  GET    /pedidos/            → listar pedidos (con filtros opcionales)
  GET    /pedidos/{id}        → obtener pedido con sus detalles
  PATCH  /pedidos/{id}/estado → avanzar el estado del pedido
  DELETE /pedidos/{id}        → eliminar pedido (solo si está pendiente)
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.pedido import EstadoPedido
from app.schemas.pedido import PedidoCreate, PedidoUpdate, PedidoResponse, PedidoList
from app.services import pedido_service

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.post(
    "/",
    response_model=PedidoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear pedido con sus productos",
)
def crear_pedido(
    payload: PedidoCreate,
    db: Session = Depends(get_db),
) -> PedidoResponse:
    """
    Crea un pedido completo en una sola operación.

    El backend calcula automáticamente:
    - **tax_usd** por línea = `precio_base × (porcentaje_tax / 100)`
    - **comision_usd** por línea = `(precio_base + tax) × (porcentaje_comision / 100)`
    - **precio_final_usd** = `precio_base + tax + comision`
    - **subtotal_usd** por línea = `precio_final × cantidad`
    - **total_usd** del pedido = suma de subtotales
    - **total_clp** = `total_usd × valor_dolar`

    El estado inicial siempre es **pendiente**.
    """
    pedido = pedido_service.crear_pedido(db, payload)
    return pedido


@router.get(
    "/",
    response_model=list[PedidoList],
    summary="Listar pedidos",
)
def listar_pedidos(
    cliente_id: UUID | None = Query(default=None, description="Filtrar por cliente"),
    estado: EstadoPedido | None = Query(default=None, description="Filtrar por estado"),
    skip: int = Query(default=0, ge=0, description="Registros a omitir"),
    limit: int = Query(default=50, ge=1, le=200, description="Máximo de resultados"),
    db: Session = Depends(get_db),
) -> list[PedidoList]:
    """
    Lista pedidos con filtros opcionales y paginación.

    Los resultados se ordenan por **fecha de creación descendente** (más reciente primero).
    """
    return pedido_service.listar_pedidos(
        db,
        cliente_id=cliente_id,
        estado=estado,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{pedido_id}",
    response_model=PedidoResponse,
    summary="Obtener pedido con sus detalles",
)
def obtener_pedido(
    pedido_id: UUID,
    db: Session = Depends(get_db),
) -> PedidoResponse:
    """Devuelve el pedido completo incluyendo todos sus productos (detalles)."""
    return pedido_service.obtener_pedido(db, pedido_id)


@router.patch(
    "/{pedido_id}/estado",
    response_model=PedidoResponse,
    summary="Avanzar estado del pedido",
)
def actualizar_estado(
    pedido_id: UUID,
    payload: PedidoUpdate,
    db: Session = Depends(get_db),
) -> PedidoResponse:
    """
    Actualiza el estado de un pedido.

    Flujo válido: **pendiente → en_bodega → enviado**

    Retorna **422** si se intenta retroceder el estado.
    """
    return pedido_service.actualizar_estado_pedido(db, pedido_id, payload)


@router.delete(
    "/{pedido_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar pedido",
)
def eliminar_pedido(
    pedido_id: UUID,
    db: Session = Depends(get_db),
) -> None:
    """
    Elimina un pedido y todos sus detalles.

    Solo se permite eliminar pedidos en estado **pendiente**.
    Retorna **409** si el pedido ya fue procesado.
    """
    pedido_service.eliminar_pedido(db, pedido_id)
