from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .dependencies import ServiceDep
from .exceptions import OrderAlreadyCompletedError, OrderNotFoundError
from .routers import orders

app = FastAPI(
    title="Учёт заказов кофейни",
    description="Сервис учёта заказов одной кофейни: создание, просмотр, "
                "частичное обновление и отмена заказов. Данные хранятся в памяти.",
    version="1.0.0",
)

app.include_router(orders.router)


@app.get("/", tags=["Сервис"], summary="Приветственное сообщение сервиса")
def root() -> dict:
    return {"message": "Добро пожаловать в сервис учёта заказов кофейни!"}


@app.get("/info", tags=["Сервис"], summary="Название сервиса и количество заказов")
def info(service: ServiceDep) -> dict:
    return {
        "app_name": app.title,
        "orders_count": service.count_orders(),
    }


@app.exception_handler(OrderNotFoundError)
async def order_not_found_handler(request: Request, exc: OrderNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": f"Заказ с id={exc.order_id} не найден"},
    )


@app.exception_handler(OrderAlreadyCompletedError)
async def order_completed_handler(request: Request, exc: OrderAlreadyCompletedError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": f"Заказ {exc.order_id} уже выполнен и не может быть изменён"},
    )
