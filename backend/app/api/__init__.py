# Re-exporta los routers para montarlos en main.py.
# Uso: from app.api import router_clientes, router_pedidos

from .clientes import router as router_clientes  # noqa: F401
from .pedidos import router as router_pedidos  # noqa: F401

__all__ = ["router_clientes", "router_pedidos"]
