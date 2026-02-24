import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class DetallePedido(Base):
    """
    Línea de producto dentro de un Pedido.

    Reglas de cálculo (se aplican en la capa de servicio antes de persistir):

        tax_usd        = precio_base_usd * (porcentaje_tax / 100)
        comision_usd   = (precio_base_usd + tax_usd) * (porcentaje_comision / 100)
        precio_final_usd = precio_base_usd + tax_usd + comision_usd
        subtotal_usd   = precio_final_usd * cantidad

    Los valores calculados se almacenan explícitamente para evitar
    recálculos y mantener histórico ante cambios de porcentajes.
    """

    __tablename__ = "detalles_pedido"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Identificador único del detalle (UUID v4)",
    )
    pedido_id = Column(
        UUID(as_uuid=True),
        ForeignKey("pedidos.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK al pedido al que pertenece este detalle",
    )

    # -------------------------------------------------------------------------
    # Datos del producto
    # -------------------------------------------------------------------------
    nombre_producto = Column(
        String(255),
        nullable=False,
        comment="Nombre descriptivo del producto comprado",
    )
    cantidad = Column(
        Integer,
        nullable=False,
        comment="Cantidad de unidades compradas",
    )

    # -------------------------------------------------------------------------
    # Precios y porcentajes base
    # precision=12, scale=4  → cuatro decimales para mayor precisión en USD
    # -------------------------------------------------------------------------
    precio_base_usd = Column(
        Numeric(precision=12, scale=4),
        nullable=False,
        comment="Precio unitario base del producto en USD (sin impuestos ni comisión)",
    )
    porcentaje_tax = Column(
        Numeric(precision=5, scale=2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Tasa de impuesto aplicada al precio base (e.g. 10.00 = 10 %)",
    )
    porcentaje_comision = Column(
        Numeric(precision=5, scale=2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Porcentaje de comisión aplicado sobre (precio_base + tax) (e.g. 5.00 = 5 %)",
    )

    # -------------------------------------------------------------------------
    # Valores calculados persistidos
    # -------------------------------------------------------------------------
    tax_usd = Column(
        Numeric(precision=12, scale=4),
        nullable=False,
        default=Decimal("0.0000"),
        comment="Monto de impuesto por unidad: precio_base_usd * (porcentaje_tax / 100)",
    )
    comision_usd = Column(
        Numeric(precision=12, scale=4),
        nullable=False,
        default=Decimal("0.0000"),
        comment="Monto de comisión por unidad: (precio_base_usd + tax_usd) * (porcentaje_comision / 100)",
    )
    precio_final_usd = Column(
        Numeric(precision=12, scale=4),
        nullable=False,
        default=Decimal("0.0000"),
        comment="Precio unitario final: precio_base_usd + tax_usd + comision_usd",
    )
    subtotal_usd = Column(
        Numeric(precision=12, scale=2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Total de esta línea: precio_final_usd * cantidad",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Fecha y hora de creación del registro (UTC)",
    )

    # -------------------------------------------------------------------------
    # Relaciones
    # -------------------------------------------------------------------------
    pedido = relationship(
        "Pedido",
        back_populates="detalles",
        lazy="select",
    )

    # -------------------------------------------------------------------------
    # Índices adicionales
    # -------------------------------------------------------------------------
    __table_args__ = (
        Index("ix_detalles_pedido_pedido_id", "pedido_id"),
        Index("ix_detalles_pedido_nombre_producto", "nombre_producto"),
    )

    def __repr__(self) -> str:
        return (
            f"<DetallePedido id={self.id} producto={self.nombre_producto!r} "
            f"cantidad={self.cantidad} subtotal_usd={self.subtotal_usd}>"
        )
