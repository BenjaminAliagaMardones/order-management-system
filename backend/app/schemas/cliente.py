"""
Schemas Pydantic para el modelo Cliente.

Convención de nomenclatura:
  - ClienteCreate   → payload para POST /clientes
  - ClienteUpdate   → payload para PATCH /clientes/{id}
  - ClienteResponse → respuesta completa devuelta por la API
  - ClienteList     → versión resumida para listar clientes
"""

from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field, field_validator

from .common import AppBaseModel


# ---------------------------------------------------------------------------
# CREATE – payload de entrada para crear un cliente
# ---------------------------------------------------------------------------
class ClienteCreate(AppBaseModel):
    """Datos requeridos para registrar un nuevo cliente."""

    nombre: str = Field(
        ...,
        min_length=2,
        max_length=150,
        examples=["María González"],
        description="Nombre completo del cliente",
    )
    telefono: str = Field(
        ...,
        min_length=7,
        max_length=30,
        examples=["+56912345678"],
        description="Número de teléfono con código de país",
    )
    email: EmailStr | None = Field(
        default=None,
        examples=["maria@gmail.com"],
        description="Correo electrónico opcional",
    )

    @field_validator("telefono")
    @classmethod
    def telefono_solo_numeros_y_plus(cls, v: str) -> str:
        """Acepta solo dígitos, espacios, guiones y el símbolo '+'."""
        import re
        if not re.match(r"^\+?[\d\s\-]{7,30}$", v):
            raise ValueError(
                "El teléfono solo puede contener dígitos, espacios, guiones y '+'"
            )
        return v.strip()


# ---------------------------------------------------------------------------
# UPDATE – todos los campos son opcionales para PATCH parcial
# ---------------------------------------------------------------------------
class ClienteUpdate(AppBaseModel):
    """Campos que pueden actualizarse en un cliente existente."""

    nombre: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
        description="Nuevo nombre completo",
    )
    telefono: str | None = Field(
        default=None,
        min_length=7,
        max_length=30,
        description="Nuevo número de teléfono",
    )
    email: EmailStr | None = Field(
        default=None,
        description="Nuevo correo electrónico (null para eliminar)",
    )


# ---------------------------------------------------------------------------
# RESPONSE – lo que devuelve la API al consultar un cliente
# ---------------------------------------------------------------------------
class ClienteResponse(AppBaseModel):
    """Representación completa de un cliente devuelta por la API."""

    id: UUID
    nombre: str
    telefono: str
    email: EmailStr | None
    created_at: datetime


# ---------------------------------------------------------------------------
# LIST – versión resumida para listados (sin pedidos anidados)
# ---------------------------------------------------------------------------
class ClienteList(AppBaseModel):
    """Versión compacta para endpoints que devuelven múltiples clientes."""

    id: UUID
    nombre: str
    telefono: str
    email: EmailStr | None
