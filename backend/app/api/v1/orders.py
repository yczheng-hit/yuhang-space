"""点菜订单路由 — 购物车 CRUD。"""

import uuid

from fastapi import APIRouter, Query

from app.dependencies import CurrentUser, DBSession
from app.schemas.order import CartSummary, OrderCreate, OrderResponse, OrderUpdate
from app.services import order_service

router = APIRouter()


@router.post("", response_model=OrderResponse)
async def add_to_cart(data: OrderCreate, db: DBSession, user: CurrentUser):
    """添加菜品到购物车。"""
    return await order_service.add_to_cart(db, user.id, data)


@router.get("/carts", response_model=list[str])
async def list_carts(db: DBSession, user: CurrentUser):
    """列出所有购物车名称。"""
    return await order_service.list_carts(db, user.id)


@router.get("/cart", response_model=CartSummary)
async def get_cart(
    db: DBSession,
    user: CurrentUser,
    cart_name: str = Query(default="默认购物车"),
):
    """获取指定购物车的内容及汇总。"""
    return await order_service.get_cart_summary(db, user.id, cart_name)


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: uuid.UUID,
    data: OrderUpdate,
    db: DBSession,
    user: CurrentUser,
):
    """更新订单数量或备注。"""
    return await order_service.update_order(db, order_id, user.id, data)


@router.delete("/{order_id}")
async def delete_order(order_id: uuid.UUID, db: DBSession, user: CurrentUser):
    """删除单个订单。"""
    await order_service.delete_order(db, order_id, user.id)
    return {"detail": "已删除"}


@router.delete("/cart/{cart_name}")
async def clear_cart(cart_name: str, db: DBSession, user: CurrentUser):
    """一键清空指定购物车。"""
    count = await order_service.clear_cart(db, user.id, cart_name)
    return {"detail": f"已清空 {count} 项"}
