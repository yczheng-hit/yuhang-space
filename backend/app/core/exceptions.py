"""自定义异常类 + 全局异常处理器。"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """应用基础异常。"""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class NotFoundException(AppException):
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(status_code=404, detail=detail)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "未授权"):
        super().__init__(status_code=401, detail=detail)


class BadRequestException(AppException):
    def __init__(self, detail: str = "请求无效"):
        super().__init__(status_code=400, detail=detail)


class ConflictException(AppException):
    def __init__(self, detail: str = "资源冲突"):
        super().__init__(status_code=409, detail=detail)


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器。"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
