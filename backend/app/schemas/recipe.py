"""菜谱相关 Pydantic 模型。"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class IngredientItem(BaseModel):
    name: str
    amount: str
    unit: str


class LinkItem(BaseModel):
    url: str
    comment: str = ""


class RecipeCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str | None = None
    ingredients: list[IngredientItem] = []
    instructions: list[str] = []
    prep_time_min: int | None = None
    cook_time_min: int | None = None
    servings: int | None = None
    tags: list[str] = []
    price: float = 0.0
    links: list[LinkItem] = []
    ai_generated: bool = False


class RecipeUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = None
    ingredients: list[IngredientItem] | None = None
    instructions: list[str] | None = None
    prep_time_min: int | None = None
    cook_time_min: int | None = None
    servings: int | None = None
    tags: list[str] | None = None
    price: float | None = None
    links: list[LinkItem] | None = None


class RecipeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None
    ingredients: list[dict]
    instructions: list[str]
    prep_time_min: int | None
    cook_time_min: int | None
    servings: int | None
    tags: list[str]
    price: float
    links: list[dict]
    ai_generated: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
