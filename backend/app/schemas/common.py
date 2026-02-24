"""
Configuración base compartida por todos los schemas del proyecto.

Se usa Pydantic v2 (model_config) que viene incluido con FastAPI >= 0.100.
"""

from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    """
    Base común para todos los schemas de respuesta.

    ``from_attributes=True`` permite crear instancias directamente desde
    objetos ORM de SQLAlchemy (antes conocido como ``orm_mode = True``).
    """

    model_config = ConfigDict(from_attributes=True)
