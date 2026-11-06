from .schemas import Order


class OrderRepository:
    """Хранит заказы в памяти. Никакой бизнес-логики — только доступ к данным."""

    def __init__(self) -> None:
        self._orders: dict[int, Order] = {}
        self._next_id = 1

    def get_all(self) -> list[Order]:
        return list(self._orders.values())

    def get_by_id(self, order_id: int) -> Order | None:
        return self._orders.get(order_id)

    def add(self, order: Order) -> Order:
        # Счётчик никогда не уменьшается, поэтому id не повторяются после удаления.
        order.id = self._next_id
        self._orders[order.id] = order
        self._next_id += 1
        return order

    def update(self, order_id: int, update_data: dict) -> Order | None:
        order = self._orders.get(order_id)
        if order is None:
            return None
        for field, value in update_data.items():
            setattr(order, field, value)
        return order

    def delete(self, order_id: int) -> bool:
        if order_id not in self._orders:
            return False
        del self._orders[order_id]
        return True
