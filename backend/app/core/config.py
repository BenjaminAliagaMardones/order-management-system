"""
Configuración y variables de entorno del backend.

Lee el archivo .env automáticamente gracias a python-dotenv.
Luego expone las variables tipadas para que el resto de la app
las importe desde aquí, evitando llamadas a os.getenv dispersas.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carga el .env que está en la raíz del proyecto (un nivel arriba de /backend)
_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=_ENV_FILE if _ENV_FILE.exists() else None)


# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.environ["DATABASE_URL"]
# Ejemplo esperado en .env:
#   DATABASE_URL=postgresql://postgres:postgres@db:5432/shop_db


# ---------------------------------------------------------------------------
# Aplicación
# ---------------------------------------------------------------------------
APP_TITLE: str = os.getenv("APP_TITLE", "Order Management System")
APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
# Ejemplo en .env:
#   CORS_ORIGINS=https://mi-frontend.onrender.com,http://localhost:5173
_raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
CORS_ORIGINS: list[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]
