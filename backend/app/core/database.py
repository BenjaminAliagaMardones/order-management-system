"""
Sesión de base de datos con SQLAlchemy.

Exporta:
  - engine        → conexión al servidor PostgreSQL
  - SessionLocal  → fábrica de sesiones
  - get_db        → dependencia FastAPI (yield) para inyectar la sesión
                    en los endpoints vía Depends(get_db)
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import DATABASE_URL

# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
# connect_args no es necesario en psycopg2, pero se deja el patrón claro.
# pool_pre_ping=True verifica la conexión antes de usarla (útil con Docker).
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    # pool_size y max_overflow se pueden ajustar por variables de entorno
    # si el proyecto crece a producción.
    pool_size=5,
    max_overflow=10,
    echo=True,   # TEMPORAL: ver queries SQL en Render logs para debug
)

# ---------------------------------------------------------------------------
# Fábrica de sesiones
# ---------------------------------------------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,   # Siempre usar commit() explícito
    autoflush=False,    # No flushear automáticamente antes de queries
    expire_on_commit=False,  # Los objetos siguen accesibles después del commit
)


# ---------------------------------------------------------------------------
# Dependencia FastAPI
# ---------------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """
    Dependencia de FastAPI que provee una sesión de SQLAlchemy por request.

    Uso en un endpoint:

        from fastapi import Depends
        from sqlalchemy.orm import Session
        from app.core.database import get_db

        @router.get("/ejemplo")
        def mi_endpoint(db: Session = Depends(get_db)):
            ...

    La sesión se cierra automáticamente al finalizar el request,
    incluso si se lanza una excepción.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
