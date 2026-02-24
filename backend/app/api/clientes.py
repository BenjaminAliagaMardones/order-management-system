"""
Router de Clientes.

Endpoints:
  POST   /clientes/           → crear cliente
  GET    /clientes/           → listar clientes (paginado)
  GET    /clientes/{id}       → obtener cliente por ID
  PATCH  /clientes/{id}       → actualizar campos del cliente
  DELETE /clientes/{id}       → eliminar cliente (si no tiene pedidos)
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse, ClienteList
from app.services import cliente_service

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post(
    "/",
    response_model=ClienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo cliente",
)
def crear_cliente(
    payload: ClienteCreate,
    db: Session = Depends(get_db),
) -> ClienteResponse:
    """
    Registra un nuevo cliente en el sistema.

    - **nombre**: nombre completo (requerido)
    - **telefono**: con código de país, ej: +56912345678
    - **email**: opcional; si se provee no puede estar duplicado
    """
    cliente = cliente_service.crear_cliente(db, payload)
    return cliente


@router.get(
    "/",
    response_model=list[ClienteList],
    summary="Listar clientes",
)
def listar_clientes(
    skip: int = Query(default=0, ge=0, description="Registros a omitir"),
    limit: int = Query(default=50, ge=1, le=200, description="Máximo de resultados"),
    db: Session = Depends(get_db),
) -> list[ClienteList]:
    """Devuelve la lista de clientes ordenada por nombre, con paginación."""
    return cliente_service.listar_clientes(db, skip=skip, limit=limit)


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Obtener cliente por ID",
)
def obtener_cliente(
    cliente_id: UUID,
    db: Session = Depends(get_db),
) -> ClienteResponse:
    """Devuelve los datos completos de un cliente dado su UUID."""
    return cliente_service.obtener_cliente(db, cliente_id)


@router.patch(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Actualizar cliente",
)
def actualizar_cliente(
    cliente_id: UUID,
    payload: ClienteUpdate,
    db: Session = Depends(get_db),
) -> ClienteResponse:
    """
    Actualización parcial de un cliente (PATCH).

    Solo se modifican los campos incluidos en el body.
    """
    return cliente_service.actualizar_cliente(db, cliente_id, payload)


@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar cliente",
)
def eliminar_cliente(
    cliente_id: UUID,
    db: Session = Depends(get_db),
) -> None:
    """
    Elimina un cliente.

    Retorna **409** si el cliente tiene pedidos asociados.
    """
    cliente_service.eliminar_cliente(db, cliente_id)
