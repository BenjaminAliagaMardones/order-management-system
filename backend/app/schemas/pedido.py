"""
Schemas Pydantic para el modelo Pedido.

Convención:
  - PedidoCreate        → payload para POST /pedidos
  - PedidoUpdate        → payload para PATCH /pedidos/{id} (solo estado)
  - PedidoResponse      → respuesta completa con detalles anidados
  - PedidoList          → versión resumida sin detalles anidados
  - PedidoConDetalles   → respuesta completa con lista de DetallePedido
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field, field_validator

from app.models.pedido import EstadoPedido
from .common import AppBaseModel
from .detalle_pedido import DetallePedidoCreate, DetallePedidoResponse


# ---------------------------------------------------------------------------
# CREATE – payload completo para crear un pedido con sus detalles
# ---------------------------------------------------------------------------
class PedidoCreate(AppBaseModel):
    """
    Datos para crear un pedido nuevo.

    La shopper envía:
    - el ID del cliente
    - el tipo de cambio del día (valor_dolar)
    - la lista de productos comprados

    Los totales (subtotal_usd, total_usd, total_clp) los calcula el servicio.
    """

    cliente_id: UUID = Field(
        ...,
        description="UUID del cliente que realizó el pedido",
    )
    valor_dolar: Decimal = Field(
        ...,
        gt=Decimal("0"),
        decimal_places=2,
        examples=[Decimal("970.50")],
        description="Tipo de cambio USD→CLP vigente al momento de crear el pedido",
    )
    detalles: list[DetallePedidoCreate] = Field(
        ...,
        min_length=1,
        description="Lista de productos del pedido (mínimo 1 ítem)",
    )

    @field_validator("valor_dolar", mode="before")
    @classmethod
    def convertir_a_decimal(cls, v: object) -> Decimal:
        return Decimal(str(v))


# ---------------------------------------------------------------------------
# UPDATE – solo permite cambiar el estado del pedido (flujo de la shopper)
# ---------------------------------------------------------------------------
class PedidoUpdate(AppBaseModel):
    """
    Actualización parcial del pedido.

    Por diseño, una vez creado un pedido solo se actualiza su estado:
      pendiente → en_bodega → enviado
    """

    estado: EstadoPedido = Field(
        ...,
        description="Nuevo estado del pedido",
        examples=[EstadoPedido.EN_BODEGA],
    )


# ---------------------------------------------------------------------------
# RESPONSE – versión resumida sin lista de detalles (para listados)
# ---------------------------------------------------------------------------
class PedidoList(AppBaseModel):
    """Vista resumida del pedido para endpoints de listado."""

    id: UUID
    cliente_id: UUID
    estado: EstadoPedido
    subtotal_usd: Decimal
    total_usd: Decimal
    valor_dolar: Decimal
    total_clp: Decimal
    created_at: datetime


# ---------------------------------------------------------------------------
# RESPONSE COMPLETO – incluye los detalles anidados
# ---------------------------------------------------------------------------
class PedidoResponse(AppBaseModel):
    """
    Respuesta completa del pedido con todos sus detalles.

    Usar este schema en:
      GET /pedidos/{id}
      POST /pedidos  (respuesta de creación)
    """

    id: UUID
    cliente_id: UUID
    estado: EstadoPedido
    subtotal_usd: Decimal
    total_usd: Decimal
    valor_dolar: Decimal
    total_clp: Decimal
    created_at: datetime

    # Detalles anidados – requiere lazy=False o eager loading en el endpoint
    detalles: list[DetallePedidoResponse] = Field(default_factory=list)
