"""认证业务逻辑。"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ConflictException, UnauthorizedException
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.security.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.security.password import hash_password, validate_password_strength, verify_password


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """按 ID 查询用户。"""
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        return None
    result = await db.execute(select(User).where(User.id == uid))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """按用户名查询用户。"""
    result = await db.execute(
        select(User).where(User.username == username.lower())
    )
    return result.scalar_one_or_none()


async def register(db: AsyncSession, req: RegisterRequest) -> User:
    """注册新用户。"""
    try:
        validate_password_strength(req.password)
    except ValueError as e:
        raise BadRequestException(str(e)) from e

    # 检查用户名唯一性
    existing = await db.execute(
        select(User).where(User.username == req.username.lower())
    )
    if existing.scalar_one_or_none() is not None:
        raise ConflictException("用户名已被注册")

    user = User(
        username=req.username.lower(),
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login(db: AsyncSession, username: str, password: str, remember_me: bool = False) -> dict:
    """登录并返回 Token。remember_me 时 refresh_token 有效期延长到 90 天。"""
    user = await get_user_by_username(db, username)
    if user is None or not verify_password(password, user.hashed_password):
        raise UnauthorizedException("用户名或密码错误")
    if not user.is_active:
        raise UnauthorizedException("账户已禁用")

    refresh_days = 90 if remember_me else None
    return {
        "access_token": create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id), days=refresh_days),
        "token_type": "bearer",
    }


async def refresh(db: AsyncSession, refresh_token: str) -> dict:
    """刷新 Access Token。"""
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise UnauthorizedException("Refresh Token 无效或已过期")

    user = await get_user_by_id(db, payload["sub"])
    if user is None or not user.is_active:
        raise UnauthorizedException("用户不存在或已禁用")

    return {
        "access_token": create_access_token(str(user.id)),
        "token_type": "bearer",
    }
