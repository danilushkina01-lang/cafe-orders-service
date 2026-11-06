class OrderNotFoundError(Exception):
    def __init__(self, order_id: int):
        self.order_id = order_id
        super().__init__(f"Заказ с id={order_id} не найден")


class OrderAlreadyCompletedError(Exception):
    def __init__(self, order_id: int):
        self.order_id = order_id
        super().__init__(f"Заказ {order_id} уже выполнен и не может быть изменён")
