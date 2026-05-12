"""运维 API HMAC 签名验证。"""

import hashlib
import hmac
import time
from typing import Annotated

from fastapi import Header, HTTPException, Request

from app.config import settings
from app.core.constants import MAINTENANCE_TIMESTAMP_MAX_AGE_SECONDS


async def verify_maintenance_auth(
    request: Request,
    x_maintenance_key: Annotated[str, Header()] = "",
    x_timestamp: Annotated[str, Header()] = "",
    x_signature: Annotated[str, Header()] = "",
) -> None:
    """FastAPI 依赖：验证运维 API 的 HMAC 签名。"""
    # 第一层：IP 白名单
    client_ip = request.client.host if request.client else ""
    if client_ip not in settings.allowed_maintenance_ips_list:
        raise HTTPException(status_code=403, detail="IP 不在白名单中")

    # 第二层：时间戳防重放
    try:
        ts = int(x_timestamp)
    except (ValueError, TypeError):
        raise HTTPException(status_code=403, detail="时间戳无效") from None

    now = int(time.time())
    if abs(now - ts) > MAINTENANCE_TIMESTAMP_MAX_AGE_SECONDS:
        raise HTTPException(status_code=403, detail="请求已过期")

    # 第三层：HMAC 签名验证
    body = await request.body()
    message = f"{x_timestamp}.{request.method}.{request.url.path}".encode()
    expected = hmac.new(
        settings.MAINTENANCE_API_KEY.encode(),
        message + body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, x_signature):
        raise HTTPException(status_code=403, detail="签名验证失败")
