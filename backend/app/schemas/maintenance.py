"""运维相关 Pydantic 模型。"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


class StatsResponse(BaseModel):
    total_users: int
    total_schedules: int
    total_recipes: int
    total_media_files: int


class CleanupResponse(BaseModel):
    deleted_count: int
    message: str
