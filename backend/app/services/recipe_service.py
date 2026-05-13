"""菜谱业务逻辑。"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeUpdate


async def create_recipe(
    db: AsyncSession, user_id: uuid.UUID, data: RecipeCreate
) -> Recipe:
    """创建菜谱。"""
    recipe = Recipe(
        user_id=user_id,
        title=data.title,
        description=data.description,
        ingredients=[i.model_dump() for i in data.ingredients],
        instructions=data.instructions,
        prep_time_min=data.prep_time_min,
        cook_time_min=data.cook_time_min,
        servings=data.servings,
        tags=data.tags,
        price=data.price,
        links=[lnk.model_dump() for lnk in data.links],
        ai_generated=data.ai_generated,
    )
    db.add(recipe)
    await db.commit()
    await db.refresh(recipe)
    return recipe


async def get_recipe(
    db: AsyncSession, recipe_id: uuid.UUID, user_id: uuid.UUID
) -> Recipe:
    """获取单个菜谱（校验所有权）。"""
    result = await db.execute(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.user_id == user_id)
    )
    recipe = result.scalar_one_or_none()
    if recipe is None:
        raise NotFoundException("菜谱不存在")
    return recipe


async def list_recipes(
    db: AsyncSession, user_id: uuid.UUID, skip: int = 0, limit: int = 50
) -> list[Recipe]:
    """列出用户的所有菜谱。"""
    result = await db.execute(
        select(Recipe)
        .where(Recipe.user_id == user_id)
        .order_by(Recipe.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_recipe(
    db: AsyncSession, recipe_id: uuid.UUID, user_id: uuid.UUID, data: RecipeUpdate
) -> Recipe:
    """更新菜谱。"""
    recipe = await get_recipe(db, recipe_id, user_id)
    update_data = data.model_dump(exclude_unset=True)
    if "ingredients" in update_data and update_data["ingredients"] is not None:
        update_data["ingredients"] = [
            i.model_dump() if hasattr(i, "model_dump") else i
            for i in update_data["ingredients"]
        ]
    if "links" in update_data and update_data["links"] is not None:
        update_data["links"] = [
            lnk.model_dump() if hasattr(lnk, "model_dump") else lnk
            for lnk in update_data["links"]
        ]
    for field, value in update_data.items():
        setattr(recipe, field, value)
    await db.commit()
    await db.refresh(recipe)
    return recipe


async def delete_recipe(
    db: AsyncSession, recipe_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    """删除菜谱。"""
    recipe = await get_recipe(db, recipe_id, user_id)
    await db.delete(recipe)
    await db.commit()
