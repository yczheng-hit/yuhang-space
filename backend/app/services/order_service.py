"""点菜订单业务逻辑。"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.order import Order
from app.models.recipe import Recipe
from app.schemas.order import OrderCreate, OrderUpdate


async def add_to_cart(
    db: AsyncSession, user_id: uuid.UUID, data: OrderCreate
) -> Order:
    """添加菜品到购物车。"""
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
        status="cart",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def get_cart(
    db: AsyncSession, user_id: uuid.UUID, cart_name: str = "默认购物车"
) -> list[Order]:
    """获取指定购物车的所有订单（仅 cart 状态）。"""
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id, Order.cart_name == cart_name, Order.status == "cart")
        .order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())


async def list_carts(
    db: AsyncSession, user_id: uuid.UUID
) -> list[str]:
    """列出用户的所有购物车名称（仅 cart 状态）。"""
    result = await db.execute(
        select(distinct(Order.cart_name))
        .where(Order.user_id == user_id, Order.status == "cart")
        .order_by(Order.cart_name)
    )
    return [row[0] for row in result.all()]


async def list_submitted_batches(
    db: AsyncSession, user_id: uuid.UUID
) -> list[dict]:
    """列出用户已提交的历史订单批次，按提交时间分组。"""
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id, Order.status == "submitted")
        .order_by(Order.submitted_at.desc())
    )
    all_orders = list(result.scalars().all())

    # Group by submitted_at timestamp
    batches = {}
    for order in all_orders:
        key = order.submitted_at.isoformat() if order.submitted_at else "unknown"
        if key not in batches:
            batches[key] = {
                "submitted_at": order.submitted_at,
                "cart_name": order.cart_name,
                "item_count": 0,
                "total_price": 0.0,
            }
        batches[key]["item_count"] += 1
        batches[key]["total_price"] += order.unit_price * order.quantity
        # Use the latest cart_name in the batch
        batches[key]["cart_name"] = order.cart_name

    # Sort by submitted_at descending, None values go last
    def sort_key(x):
        if x["submitted_at"] is None:
            return (0, "")
        return (1, x["submitted_at"].isoformat())
    return sorted(batches.values(), key=sort_key, reverse=True)


async def get_submitted_batch(
    db: AsyncSession, user_id: uuid.UUID, submitted_at: str
) -> dict:
    """获取指定提交时间的历史订单详情。"""
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id, Order.status == "submitted")
        .order_by(Order.submitted_at.desc())
    )
    all_orders = list(result.scalars().all())

    # Find orders matching the submitted_at batch
    batch_orders = []
    for order in all_orders:
        if order.submitted_at and order.submitted_at.isoformat() == submitted_at:
            batch_orders.append(order)

    total_price = sum(o.unit_price * o.quantity for o in batch_orders)
    cart_name = batch_orders[0].cart_name if batch_orders else ""
    return {
        "cart_name": cart_name,
        "submitted_at": submitted_at,
        "items": batch_orders,
        "total_price": total_price,
        "item_count": len(batch_orders),
    }


async def delete_submitted_batch(
    db: AsyncSession, user_id: uuid.UUID, submitted_at: str
) -> int:
    """删除指定提交时间的历史订单。"""
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id, Order.status == "submitted")
    )
    all_orders = list(result.scalars().all())

    count = 0
    for order in all_orders:
        if order.submitted_at and order.submitted_at.isoformat() == submitted_at:
            await db.delete(order)
            count += 1
    await db.commit()
    return count


async def submit_cart(
    db: AsyncSession, user_id: uuid.UUID, cart_name: str
) -> int:
    """提交购物车：将 cart 状态改为 submitted，记录提交时间。"""
    orders = await get_cart(db, user_id, cart_name)
    if not orders:
        raise NotFoundException("购物车为空")
    now = datetime.now(UTC)
    for order in orders:
        order.status = "submitted"
        order.submitted_at = now
    await db.commit()
    return len(orders)


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
    """清空指定购物车（仅 cart 状态），返回删除的订单数量。"""
    result = await db.execute(
        select(Order).where(
            Order.user_id == user_id, Order.cart_name == cart_name, Order.status == "cart"
        )
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
