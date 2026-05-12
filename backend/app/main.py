"""FastAPI 应用入口 — 工厂模式，生命周期管理。"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, Response

from app.config import settings
from app.core.exceptions import register_exception_handlers

# 前端构建产物目录
FRONTEND_DIR = (Path(__file__).resolve().parent.parent.parent / "frontend" / "dist").resolve()

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

# 静态文件挂载（媒体文件访问）
app.mount("/media", StaticFiles(directory=str(settings.media_root_path)), name="media")

# 注册路由
from app.api.v1.router import api_router  # noqa: E402

app.include_router(api_router, prefix="/api/v1")

# 前端静态文件服务
if FRONTEND_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="frontend-assets")


class SPAMiddleware(BaseHTTPMiddleware):
    """SPA fallback：非 API/媒体/静态资源的 GET 请求返回 index.html。"""

    SKIP_PREFIXES = ("/api/", "/media/", "/assets/", "/docs", "/openapi.json", "/redoc")

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # 仅对 GET 404 响应做 SPA fallback
        if (
            request.method == "GET"
            and response.status_code == 404
            and not any(request.url.path.startswith(p) for p in self.SKIP_PREFIXES)
        ):
            index_file = FRONTEND_DIR / "index.html"
            if index_file.is_file():
                return FileResponse(str(index_file))
        return response


app.add_middleware(SPAMiddleware)
