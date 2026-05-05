"""认证路由 — 注册、登录、刷新 Token。"""

from fastapi import APIRouter

from app.dependencies import DBSession
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services import auth_service

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(req: RegisterRequest, db: DBSession):
    """用户注册。"""
    user = await auth_service.register(db, req)
    return UserResponse(user_id=user.id, username=user.username)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: DBSession):
    """用户登录。"""
    return await auth_service.login(db, req.username, req.password)


@router.post("/refresh", response_model=dict)
async def refresh(req: RefreshRequest, db: DBSession):
    """刷新 Access Token。"""
    return await auth_service.refresh(db, req.refresh_token)
