from fastapi import FastAPI

from app.core.config import APP_TITLE, APP_VERSION, DEBUG
from app.api import router_clientes, router_pedidos

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    debug=DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    description=(
        "API para gestión de pedidos de una shopper que vende productos "
        "desde EE.UU. a Chile. Incluye cálculo automático de impuestos, "
        "comisiones y conversión USD→CLP."
    ),
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(router_clientes, prefix="/api/v1")
app.include_router(router_pedidos, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "version": APP_VERSION}