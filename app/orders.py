from typing import Annotated, Optional

from fastapi import APIRouter, Query, Response, status

from ..dependencies import PaginationDep, ServiceDep
from ..schemas import Order, OrderCreate, OrderStatus, OrderUpdate

router = APIRouter(prefix="/orders", tags=["Заказы"])


@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED,
             summary="Создать новый заказ")
def create_order(order: OrderCreate, service: ServiceDep) -> Order:
    return service.create_order(order)


@router.get("", response_model=list[Order],
            summary="Список заказов с фильтром, сортировкой и постраничной выдачей")
def list_orders(
    service: ServiceDep,
    pagination: PaginationDep,
    status_filter: Annotated[OrderStatus | None, Query(alias="status")] = None,
    sort_by: Annotated[Optional[str], Query()] = None,
) -> list[Order]:
    return service.list_orders(status=status_filter, sort_by=sort_by, **pagination)


@router.get("/{order_id}", response_model=Order,
            summary="Получить заказ по идентификатору")
def get_order(order_id: int, service: ServiceDep) -> Order:
    return service.get_order(order_id)


@router.patch("/{order_id}", response_model=Order,
              summary="Частично обновить заказ")
def update_order(order_id: int, update: OrderUpdate, service: ServiceDep) -> Order:
    return service.update_order(order_id, update)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Отменить (удалить) заказ")
def cancel_order(order_id: int, service: ServiceDep) -> Response:
    service.cancel_order(order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
