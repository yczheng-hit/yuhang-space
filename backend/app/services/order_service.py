"""点菜订单业务逻辑。"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.order import Order
from app.models.recipe import Recipe
from app.schemas.order import OrderCreate, OrderUpdate


async def add_to_cart(
    db: AsyncSession, user_id: uuid.UUID, data: OrderCreate
) -> Order:
    """添加菜品到购物车。"""
    # 获取菜谱信息以获取价格
    result = await db.execute(
        select(Recipe).where(Recipe.id == data.recipe_id)
    )
    recipe = result.scalar_one_or_none()
    if recipe is None:
        raise NotFoundException("菜谱不存在")

    order = Order(
        user_id=user_id,
        recipe_id=data.recipe_id,
        cart_name=data.cart_name,
        quantity=data.quantity,
        unit_price=recipe.price,
        note=data.note,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def get_cart(
    db: AsyncSession, user_id: uuid.UUID, cart_name: str = "默认购物车"
) -> list[Order]:
    """获取指定购物车的所有订单。"""
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id, Order.cart_name == cart_name)
        .order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())


async def list_carts(
    db: AsyncSession, user_id: uuid.UUID
) -> list[str]:
    """列出用户的所有购物车名称。"""
    from sqlalchemy import distinct
    result = await db.execute(
        select(distinct(Order.cart_name))
        .where(Order.user_id == user_id)
        .order_by(Order.cart_name)
    )
    return [row[0] for row in result.all()]


async def update_order(
    db: AsyncSession, order_id: uuid.UUID, user_id: uuid.UUID, data: OrderUpdate
) -> Order:
    """更新订单数量或备注。"""
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user_id)
    )
    order = result.scalar_one_or_none()
    if order is None:
        raise NotFoundException("订单不存在")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    await db.commit()
    await db.refresh(order)
    return order


async def delete_order(
    db: AsyncSession, order_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    """删除单个订单。"""
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.user_id == user_id)
    )
    order = result.scalar_one_or_none()
    if order is None:
        raise NotFoundException("订单不存在")
    await db.delete(order)
    await db.commit()


async def clear_cart(
    db: AsyncSession, user_id: uuid.UUID, cart_name: str
) -> int:
    """清空指定购物车，返回删除的订单数量。"""
    result = await db.execute(
        select(Order).where(Order.user_id == user_id, Order.cart_name == cart_name)
    )
    orders = list(result.scalars().all())
    count = len(orders)
    for order in orders:
        await db.delete(order)
    await db.commit()
    return count


async def get_cart_summary(
    db: AsyncSession, user_id: uuid.UUID, cart_name: str
) -> dict:
    """获取购物车汇总信息。"""
    orders = await get_cart(db, user_id, cart_name)
    total_price = sum(o.unit_price * o.quantity for o in orders)
    return {
        "cart_name": cart_name,
        "items": orders,
        "total_price": total_price,
        "item_count": len(orders),
    }
