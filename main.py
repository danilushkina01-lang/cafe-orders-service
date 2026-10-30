from fastapi import FastAPI, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict


# --- Настройки через .env ---
class Settings(BaseSettings):
    app_name: str
    default_page_size: int = 10
    max_page_size: int = 50

    class Config:
        env_prefix = "APP_"  # если хочешь префикс APP_ в .env; в задании префикса нет, поэтому можно убрать, но оставим для ясности
        # Если не хочешь префикс, используй env_file и читай переменные как есть.

    # Чтобы читать переменные без префикса APP_, переопределим чтение:
    @classmethod
    def settings_customise_env(cls):
        return {"env_file": ".env", "env_file_encoding": "utf-8"}


# Для задания проще читать переменные как есть, без префикса. Переопределим Settings так:
class AppSettings(BaseSettings):
    app_name: str
    default_page_size: int = 10
    max_page_size: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# --- Перечисления (Enum) ---
class DrinkSize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"


class OrderStatus(str, Enum):
    pending = "pending"
    ready = "ready"
    completed = "completed"
    cancelled = "cancelled"


# --- Модели данных (Pydantic) ---
class OrderCreate(BaseModel):
    drink: str = Field(..., description="Название напитка из меню", examples=["Латте", "Капучино"])
    size: DrinkSize = Field(..., description="Размер напитка", examples=["small", "medium", "large"])
    quantity: int = Field(..., gt=0, description="Количество порций, положительное число", examples=[1, 2])
    customer_name: Optional[str] = Field(None, description="Имя клиента (необязательно)", examples=["Ирина"])


class OrderUpdate(BaseModel):
    drink: Optional[str] = Field(None, description="Новое название напитка")
    size: Optional[DrinkSize] = Field(None, description="Новый размер напитка")
    quantity: Optional[int] = Field(None, gt=0, description="Новое количество порций")
    customer_name: Optional[str] = Field(None, description="Новое имя клиента")
    status: Optional[OrderStatus] = Field(None, description="Новый статус заказа")


class OrderResponse(BaseModel):
    id: int
    drink: str
    size: DrinkSize
    quantity: int
    customer_name: Optional[str]
    status: OrderStatus
    created_at: datetime


# --- Хранилище в памяти ---
# Используем словарь для быстрого поиска по ID и отдельный счётчик ID, чтобы не повторять ID после удалений.
orders_db: Dict[int, dict] = {}
next_id_counter = 1


def get_settings() -> AppSettings:
    return AppSettings()


app = FastAPI(
    title="Учёт заказов кофейни",
    description="Простой сервис для учёта заказов в кофейне: создание, просмотр, обновление, удаление заказов. Данные хранятся в памяти.",
    version="1.0.0"
)


@app.get("/", tags=["Сервис"], summary="Приветственное сообщение сервиса")
def root():
    return {"message": "Добро пожаловать в сервис учёта заказов кофейни!"}


@app.get("/info", tags=["Сервис"], summary="Информация о сервисе и текущем количестве заказов")
def info(settings: AppSettings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "total_orders": len(orders_db),
        "default_page_size": settings.default_page_size,
        "max_page_size": settings.max_page_size
    }


@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Заказы"],
          summary="Создать новый заказ")
def create_order(order: OrderCreate):
    global next_id_counter
    new_order = {
        "id": next_id_counter,
        "drink": order.drink,
        "size": order.size,
        "quantity": order.quantity,
        "customer_name": order.customer_name,
        "status": OrderStatus.pending,
        "created_at": datetime.now()
    }
    orders_db[next_id_counter] = new_order
    next_id_counter += 1
    return new_order


@app.get("/orders", response_model=List[OrderResponse], tags=["Заказы"], summary="Список заказов с фильтрацией и пагинацией")
def list_orders(
    status: Optional[OrderStatus] = Query(None, description="Фильтр по статусу заказа"),
    limit: int = Query(default=10, le=50, description="Максимальное количество заказов на странице, не более 50"),
    offset: int = Query(default=0, ge=0, description="Смещение для пагинации")
):
    # Фильтрация по статусу
    filtered = list(orders_db.values())
    if status is not None:
        filtered = [o for o in filtered if o["status"] == status]

    # Пагинация
    total = len(filtered)
    paginated = filtered[offset:offset + limit]

    return paginated


@app.get("/orders/{order_id}", response_model=OrderResponse, tags=["Заказы"], summary="Получить заказ по идентификатору")
def get_order(order_id: int):
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    return order


@app.patch("/orders/{order_id}", response_model=OrderResponse, tags=["Заказы"], summary="Частично обновить заказ")
def update_order(order_id: int, update: OrderUpdate):
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")

    # Обновляем только те поля, которые прислал клиент
    data = update.model_dump(exclude_unset=True)
    for key, value in data.items():
        if key == "status" and isinstance(value, str):
            # Приводим к типу Enum, если нужно
            order[key] = OrderStatus(value)
        else:
            order[key] = value

    return order


@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Заказы"], summary="Удалить заказ")
def delete_order(order_id: int):
    if order_id not in orders_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден")
    del orders_db[order_id]
    # Не возвращаем тело ответа — статус 204 уже задан
