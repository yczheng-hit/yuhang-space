"""FastAPI 应用入口 — 工厂模式，生命周期管理。"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.exceptions import register_exception_handlers

# 确保媒体目录存在
settings.media_root_path.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化资源，关闭时清理。"""
    yield


app = FastAPI(
    title="寰宇智杭 - 智能生活管理平台",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理器
register_exception_handlers(app)

# 静态文件挂载（开发环境提供媒体文件访问）
app.mount("/media", StaticFiles(directory=str(settings.media_root_path)), name="media")

# 注册路由
from app.api.v1.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api/v1")
