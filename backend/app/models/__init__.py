# Re-exporta Base y todos los modelos desde un único punto de entrada.
# Esto garantiza que Alembic y SQLAlchemy descubran las tablas automáticamente
# cuando se haga: from app.models import Base

from .base import Base  # noqa: F401
from .cliente import Cliente  # noqa: F401
from .pedido import EstadoPedido, Pedido  # noqa: F401
from .detalle_pedido import DetallePedido  # noqa: F401

__all__ = [
    "Base",
    "Cliente",
    "EstadoPedido",
    "Pedido",
    "DetallePedido",
]