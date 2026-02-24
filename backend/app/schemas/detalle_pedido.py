"""
Schemas Pydantic para el modelo DetallePedido.

Se define antes que PedidoResponse para poder usarlo como tipo anidado.

Convención:
  - DetallePedidoCreate   → payload para agregar un producto al pedido
  - DetallePedidoResponse → respuesta con todos los campos calculados
"""

from decimal import Decimal
from uuid import UUID
from datetime import datetime

from pydantic import Field, field_validator, model_validator

from .common import AppBaseModel


# ---------------------------------------------------------------------------
# CREATE – lo que el cliente envía por cada producto del pedido
# ---------------------------------------------------------------------------
class DetallePedidoCreate(AppBaseModel):
    """
    Datos necesarios para agregar un producto a un pedido.

    Los campos calculados (tax_usd, comision_usd, precio_final_usd,
    subtotal_usd) NO se reciben aquí; la capa de servicio los calcula
    usando las fórmulas del negocio y los persiste.
    """

    nombre_producto: str = Field(
        ...,
        min_length=2,
        max_length=255,
        examples=["iPhone 15 Pro Max 256GB"],
        description="Nombre del producto comprado en EE.UU.",
    )
    cantidad: int = Field(
        ...,
        ge=1,
        examples=[1],
        description="Cantidad de unidades (mínimo 1)",
    )
    precio_base_usd: Decimal = Field(
        ...,
        gt=Decimal("0"),
        decimal_places=4,
        examples=[Decimal("1199.99")],
        description="Precio unitario base en USD (sin impuestos ni comisión)",
    )
    porcentaje_tax: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0"),
        le=Decimal("100"),
        decimal_places=2,
        examples=[Decimal("10.00")],
        description="Porcentaje de impuesto a aplicar sobre precio_base (ej: 10.00 = 10 %)",
    )
    porcentaje_comision: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0"),
        le=Decimal("100"),
        decimal_places=2,
        examples=[Decimal("5.00")],
        description="Porcentaje de comisión a aplicar sobre (precio_base + tax) (ej: 5.00 = 5 %)",
    )

    @field_validator("precio_base_usd", "porcentaje_tax", "porcentaje_comision", mode="before")
    @classmethod
    def convertir_a_decimal(cls, v: object) -> Decimal:
        """Acepta str, int o float y los convierte a Decimal."""
        return Decimal(str(v))


# ---------------------------------------------------------------------------
# RESPONSE – devuelve todos los campos, incluyendo los calculados
# ---------------------------------------------------------------------------
class DetallePedidoResponse(AppBaseModel):
    """Línea de detalle completa con valores calculados persistidos."""

    id: UUID
    pedido_id: UUID
    nombre_producto: str
    cantidad: int

    # Campos de entrada
    precio_base_usd: Decimal
    porcentaje_tax: Decimal
    porcentaje_comision: Decimal

    # Campos calculados (capa de servicio los calcula; la BD los guarda)
    tax_usd: Decimal
    comision_usd: Decimal
    precio_final_usd: Decimal
    subtotal_usd: Decimal

    created_at: datetime
