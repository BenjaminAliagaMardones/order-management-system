# Re-exporta los módulos del core desde un único punto de entrada.
# Uso: from app.core import get_db, engine, DATABASE_URL

from .config import (  # noqa: F401
    DATABASE_URL,
    APP_TITLE,
    APP_VERSION,
    DEBUG,
)
from .database import (  # noqa: F401
    engine,
    SessionLocal,
    get_db,
)

__all__ = [
    # config
    "DATABASE_URL",
    "APP_TITLE",
    "APP_VERSION",
    "DEBUG",
    # database
    "engine",
    "SessionLocal",
    "get_db",
]
