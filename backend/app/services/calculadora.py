"""
Calculadora de precios para DetallePedido.

Toda la lógica de negocio financiera está centralizada aquí.
Los modelos y servicios llaman a estas funciones; NUNCA calculan inline.

Fórmulas:
    tax_usd          = precio_base_usd × (porcentaje_tax / 100)
    comision_usd     = (precio_base_usd + tax_usd) × (porcentaje_comision / 100)
    precio_final_usd = precio_base_usd + tax_usd + comision_usd
    subtotal_usd     = precio_final_usd × cantidad
"""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

# Precisión de redondeo para campos USD con 4 decimales
_CUATRO = Decimal("0.0001")
# Precisión de redondeo para subtotales USD con 2 decimales
_DOS = Decimal("0.01")
# Precisión para CLP (sin decimales)
_CERO = Decimal("1")


@dataclass(frozen=True)
class ResultadoDetalle:
    """
    Resultado inmutable del cálculo de precios de una línea de detalle.

    Todos los valores ya están redondeados con ROUND_HALF_UP.
    """
    tax_usd: Decimal
    comision_usd: Decimal
    precio_final_usd: Decimal
    subtotal_usd: Decimal


def calcular_detalle(
    precio_base_usd: Decimal,
    porcentaje_tax: Decimal,
    porcentaje_comision: Decimal,
    cantidad: int,
) -> ResultadoDetalle:
    """
    Calcula los campos derivados de una línea de detalle.

    Args:
        precio_base_usd:    Precio unitario base en USD.
        porcentaje_tax:     Porcentaje de impuesto (0-100).
        porcentaje_comision: Porcentaje de comisión sobre (base + tax) (0-100).
        cantidad:           Número de unidades.

    Returns:
        ResultadoDetalle con tax, comisión, precio final y subtotal.
    """
    _cien = Decimal("100")

    tax_usd = (precio_base_usd * porcentaje_tax / _cien).quantize(
        _CUATRO, rounding=ROUND_HALF_UP
    )

    comision_usd = (
        (precio_base_usd + tax_usd) * porcentaje_comision / _cien
    ).quantize(_CUATRO, rounding=ROUND_HALF_UP)

    precio_final_usd = (precio_base_usd + tax_usd + comision_usd).quantize(
        _CUATRO, rounding=ROUND_HALF_UP
    )

    subtotal_usd = (precio_final_usd * cantidad).quantize(
        _DOS, rounding=ROUND_HALF_UP
    )

    return ResultadoDetalle(
        tax_usd=tax_usd,
        comision_usd=comision_usd,
        precio_final_usd=precio_final_usd,
        subtotal_usd=subtotal_usd,
    )


def calcular_totales_pedido(
    subtotales_usd: list[Decimal],
    valor_dolar: Decimal,
) -> tuple[Decimal, Decimal, Decimal]:
    """
    Agrega los subtotales de los detalles y convierte a CLP.

    Args:
        subtotales_usd: Lista de subtotal_usd de cada DetallePedido.
        valor_dolar:    Tipo de cambio USD→CLP del día.

    Returns:
        Tupla (subtotal_usd, total_usd, total_clp).

        Nota: en este modelo subtotal_usd == total_usd porque el tax y la
        comisión ya están incluidos en precio_final_usd de cada línea.
        El campo total_usd queda separado para facilitar descuentos futuros
        a nivel de pedido.
    """
    subtotal_usd = sum(subtotales_usd, Decimal("0")).quantize(
        _DOS, rounding=ROUND_HALF_UP
    )
    total_usd = subtotal_usd  # extensible: aquí irían descuentos globales
    total_clp = (total_usd * valor_dolar).quantize(
        _CERO, rounding=ROUND_HALF_UP
    )
    return subtotal_usd, total_usd, total_clp
