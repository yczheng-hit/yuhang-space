"""点菜订单相关 Pydantic 模型。"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    recipe_id: uuid.UUID
    cart_name: str = Field(default="默认购物车", max_length=100)
    quantity: int = Field(default=1, ge=1)
    note: str | None = None


class OrderUpdate(BaseModel):
    quantity: int | None = Field(default=None, ge=1)
    note: str | None = None


class OrderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    recipe_id: uuid.UUID
    cart_name: str
    quantity: int
    unit_price: float
    note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CartSummary(BaseModel):
    cart_name: str
    items: list[OrderResponse]
    total_price: float
    item_count: int
