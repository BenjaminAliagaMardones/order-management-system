import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import APP_TITLE, APP_VERSION, DEBUG, CORS_ORIGINS
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
# CORS – permite peticiones desde el frontend (Render / localhost)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Handler global de errores 500 — muestra el traceback en debug mode
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": tb if DEBUG else "Enable DEBUG=true to see traceback"},
    )

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(router_clientes, prefix="/api/v1")
app.include_router(router_pedidos,  prefix="/api/v1")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "version": APP_VERSION}
