# Re-exporta los servicios y la calculadora desde un único punto de entrada.
# Uso: from app.services import crear_pedido, calcular_detalle, ...

from .calculadora import (  # noqa: F401
    calcular_detalle,
    calcular_totales_pedido,
    ResultadoDetalle,
)
from .cliente_service import (  # noqa: F401
    crear_cliente,
    obtener_cliente,
    listar_clientes,
    actualizar_cliente,
    eliminar_cliente,
)
from .pedido_service import (  # noqa: F401
    crear_pedido,
    obtener_pedido,
    listar_pedidos,
    actualizar_estado_pedido,
    eliminar_pedido,
)

__all__ = [
    # calculadora
    "calcular_detalle",
    "calcular_totales_pedido",
    "ResultadoDetalle",
    # cliente
    "crear_cliente",
    "obtener_cliente",
    "listar_clientes",
    "actualizar_cliente",
    "eliminar_cliente",
    # pedido
    "crear_pedido",
    "obtener_pedido",
    "listar_pedidos",
    "actualizar_estado_pedido",
    "eliminar_pedido",
]
