# Re-exporta todos los schemas desde un único punto de entrada.
# Uso en endpoints: from app.schemas import ClienteCreate, PedidoResponse, ...

from .common import AppBaseModel  # noqa: F401

from .cliente import (  # noqa: F401
    ClienteCreate,
    ClienteUpdate,
    ClienteResponse,
    ClienteList,
)

from .detalle_pedido import (  # noqa: F401
    DetallePedidoCreate,
    DetallePedidoResponse,
)

from .pedido import (  # noqa: F401
    PedidoCreate,
    PedidoUpdate,
    PedidoList,
    PedidoResponse,
)

__all__ = [
    # base
    "AppBaseModel",
    # cliente
    "ClienteCreate",
    "ClienteUpdate",
    "ClienteResponse",
    "ClienteList",
    # detalle
    "DetallePedidoCreate",
    "DetallePedidoResponse",
    # pedido
    "PedidoCreate",
    "PedidoUpdate",
    "PedidoList",
    "PedidoResponse",
]
