import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class Cliente(Base):
    """
    Representa un cliente que puede realizar múltiples pedidos.
    """

    __tablename__ = "clientes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        comment="Identificador único del cliente (UUID v4)",
    )
    nombre = Column(
        String(150),
        nullable=False,
        comment="Nombre completo del cliente",
    )
    telefono = Column(
        String(30),
        nullable=False,
        comment="Número de teléfono de contacto",
    )
    email = Column(
        String(254),
        nullable=True,
        comment="Correo electrónico opcional del cliente",
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
    pedidos = relationship(
        "Pedido",
        back_populates="cliente",
        cascade="all, delete-orphan",
        lazy="select",
    )

    # -------------------------------------------------------------------------
    # Índices adicionales
    # -------------------------------------------------------------------------
    __table_args__ = (
        Index("ix_clientes_email", "email"),
        Index("ix_clientes_telefono", "telefono"),
    )

    def __repr__(self) -> str:
        return f"<Cliente id={self.id} nombre={self.nombre!r}>"
