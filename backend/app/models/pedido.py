import uuid
from datetime import datetime
from decimal import Decimal
import enum

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class EstadoPedido(str, enum.Enum):
    """
    Estados posibles del ciclo de vida de un pedido.

    Hereda de ``str`` para que FastAPI pueda serializar el valor directamente
    como cadena de texto en las respuestas JSON.
    """

    PENDIENTE = "pendiente"
    EN_BODEGA = "en_bodega"
    ENVIADO = "enviado"


class Pedido(Base):
    """
    Pedido realizado por un Cliente.

    Los totales (subtotal_usd, total_usd, total_clp) se persisten en la base
    de datos y se calculan en la capa de servicio antes de guardar; NO se
    recalculan de forma dinámica en el modelo.
    """

    __tablename__ = "pedidos"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Identificador único del pedido (UUID v4)",
    )
    cliente_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clientes.id", ondelete="RESTRICT"),
        nullable=False,
        comment="FK al cliente que realizó el pedido",
    )
    estado = Column(
        Enum(EstadoPedido, name="estado_pedido_enum", create_type=True),
        nullable=False,
        default=EstadoPedido.PENDIENTE,
        comment="Estado actual del pedido",
    )

    # -------------------------------------------------------------------------
    # Campos monetarios  (Numeric = DECIMAL en PostgreSQL)
    # precision=12  → hasta 999 999 999,99
    # scale=2       → dos decimales para USD / CLP
    # -------------------------------------------------------------------------
    subtotal_usd = Column(
        Numeric(precision=12, scale=2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Suma de los subtotales de cada DetallePedido (en USD)",
    )
    total_usd = Column(
        Numeric(precision=12, scale=2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Total del pedido incluyendo taxes y comisiones (en USD)",
    )
    valor_dolar = Column(
        Numeric(precision=10, scale=2),
        nullable=False,
        comment="Tipo de cambio USD→CLP utilizado al crear el pedido",
    )
    total_clp = Column(
        Numeric(precision=14, scale=0),
        nullable=False,
        default=Decimal("0"),
        comment="Total del pedido convertido a pesos chilenos (CLP)",
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
    cliente = relationship(
        "Cliente",
        back_populates="pedidos",
        lazy="select",
    )
    detalles = relationship(
        "DetallePedido",
        back_populates="pedido",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # -------------------------------------------------------------------------
    # Índices adicionales
    # -------------------------------------------------------------------------
    __table_args__ = (
        Index("ix_pedidos_cliente_id", "cliente_id"),
        Index("ix_pedidos_estado", "estado"),
        Index("ix_pedidos_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Pedido id={self.id} estado={self.estado.value!r} "
            f"total_usd={self.total_usd}>"
        )
