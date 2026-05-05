"""JWT Token 创建与解析。"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt

from app.config import settings


def create_access_token(user_id: str) -> str:
    """创建短期 Access Token。"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_id, "type": "access", "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """创建长期 Refresh Token。"""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": user_id, "type": "refresh", "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[dict[str, Any]]:
    """解析 Access Token，失败返回 None。"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except jwt.PyJWTError:
        return None


def decode_refresh_token(token: str) -> Optional[dict[str, Any]]:
    """解析 Refresh Token，失败返回 None。"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except jwt.PyJWTError:
        return None
