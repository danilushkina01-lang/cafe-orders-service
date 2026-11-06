from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Query

from .config import Settings, get_settings
from .repository import OrderRepository
from .service import OrderService


@lru_cache
def get_repository() -> OrderRepository:
    return OrderRepository()


def get_service(repository: Annotated[OrderRepository, Depends(get_repository)]) -> OrderService:
    return OrderService(repository)


def pagination_params(
    settings: Annotated[Settings, Depends(get_settings)],
    limit: Annotated[int | None, Query(ge=1)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    return {
        "limit": limit if limit is not None else settings.default_page_size,
        "offset": offset,
    }


SettingsDep = Annotated[Settings, Depends(get_settings)]
ServiceDep = Annotated[OrderService, Depends(get_service)]
PaginationDep = Annotated[dict, Depends(pagination_params)]
