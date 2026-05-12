"""共享 FastAPI 依赖项。"""

from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException
from app.database import get_async_session
from app.security.jwt import decode_access_token

# 类型别名
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: DBSession = None,
):
    """从 Authorization header 解析当前用户。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedException("缺少 Bearer token")

    token = authorization.removeprefix("Bearer ")
    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedException("Token 无效或已过期")

    from app.services.auth_service import get_user_by_id

    user = await get_user_by_id(db, payload["sub"])
    if user is None:
        raise UnauthorizedException("用户不存在")
    if not user.is_active:
        raise UnauthorizedException("账户已禁用")

    return user


CurrentUser = Annotated[object, Depends(get_current_user)]
