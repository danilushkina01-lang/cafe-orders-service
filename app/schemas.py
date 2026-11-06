from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DrinkSize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"


class OrderStatus(str, Enum):
    pending = "pending"
    ready = "ready"
    completed = "completed"


class OrderCreate(BaseModel):
    drink: str = Field(
        ...,
        description="Название напитка из меню",
        examples=["Латте"],
    )
    size: DrinkSize = Field(
        ...,
        description="Размер напитка",
        examples=["medium"],
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Количество порций, положительное число",
        examples=[2],
    )
    customer_name: Optional[str] = Field(
        None,
        description="Имя клиента (необязательно)",
        examples=["Ирина"],
    )


class OrderUpdate(BaseModel):
    drink: Optional[str] = Field(None, description="Новое название напитка")
    size: Optional[DrinkSize] = Field(None, description="Новый размер напитка")
    quantity: Optional[int] = Field(None, gt=0, description="Новое количество порций")
    customer_name: Optional[str] = Field(None, description="Новое имя клиента")
    status: Optional[OrderStatus] = Field(None, description="Новый статус заказа")


class Order(BaseModel):
    id: int = Field(0, description="Идентификатор заказа")
    drink: str = Field(..., description="Название напитка из меню")
    size: DrinkSize = Field(..., description="Размер напитка")
    quantity: int = Field(..., description="Количество порций")
    customer_name: Optional[str] = Field(None, description="Имя клиента")
    status: OrderStatus = Field(..., description="Текущий статус заказа")
    created_at: datetime = Field(..., description="Момент создания заказа")
