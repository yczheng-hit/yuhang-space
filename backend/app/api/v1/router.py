"""v1 API 路由聚合。"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.schedules import router as schedules_router
from app.api.v1.recipes import router as recipes_router
from app.api.v1.llm import router as llm_router
from app.api.v1.maintenance import router as maintenance_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(schedules_router, prefix="/schedules", tags=["日程"])
api_router.include_router(recipes_router, prefix="/recipes", tags=["菜谱"])
api_router.include_router(llm_router, prefix="/llm", tags=["大模型"])
api_router.include_router(maintenance_router, prefix="/maintenance", tags=["运维"])
