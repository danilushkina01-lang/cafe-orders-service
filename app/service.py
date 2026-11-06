from datetime import datetime

from .exceptions import OrderAlreadyCompletedError, OrderNotFoundError
from .repository import OrderRepository
from .schemas import Order, OrderCreate, OrderStatus, OrderUpdate


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def create_order(self, data: OrderCreate) -> Order:
        order = Order(
            id=0,
            drink=data.drink,
            size=data.size,
            quantity=data.quantity,
            customer_name=data.customer_name,
            status=OrderStatus.pending,
            created_at=datetime.now(),
        )
        return self._repository.add(order)

    def list_orders(
        self,
        status: OrderStatus | None = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: str | None = None,
    ) -> list[Order]:
        orders = self._repository.get_all()
        if status is not None:
            orders = [o for o in orders if o.status == status]
        if sort_by is not None:
            orders.sort(key=lambda o: getattr(o, sort_by))
        return orders[offset:offset + limit]

    def get_order(self, order_id: int) -> Order:
        order = self._repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return order

    def update_order(self, order_id: int, update: OrderUpdate) -> Order:
        order = self._repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        if order.status == OrderStatus.completed:
            raise OrderAlreadyCompletedError(order_id)
        data = update.model_dump(exclude_unset=True)
        updated = self._repository.update(order_id, data)
        assert updated is not None  # заказ точно существует — проверили выше
        return updated

    def cancel_order(self, order_id: int) -> None:
        order = self._repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        if order.status == OrderStatus.completed:
            raise OrderAlreadyCompletedError(order_id)
        self._repository.delete(order_id)

    def count_orders(self) -> int:
        return len(self._repository.get_all())
