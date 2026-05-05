"""应用配置 — 从 .env 文件读取，类型化校验。"""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # 数据库
    DATABASE_URL: str = "sqlite+aiosqlite:///./yuhang_space.db"

    # JWT 认证
    JWT_SECRET_KEY: str = "CHANGE_ME_TO_A_RANDOM_64_CHAR_STRING"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 大模型配置
    LLM_ENABLED: bool = True
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL_NAME: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2048

    # 运维 API
    MAINTENANCE_API_KEY: str = "CHANGE_ME_TO_RANDOM_STRING"
    MAINTENANCE_ALLOWED_IPS: str = "127.0.0.1"

    # 媒体存储
    MEDIA_ROOT: str = "./media"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_IMAGE_TYPES: str = "jpg,jpeg,png,gif,webp"
    ALLOWED_VIDEO_TYPES: str = "mp4,mov,avi,webm"

    # 服务器
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    DEBUG: bool = True

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_image_types_list(self) -> List[str]:
        return [t.strip() for t in self.ALLOWED_IMAGE_TYPES.split(",")]

    @property
    def allowed_video_types_list(self) -> List[str]:
        return [t.strip() for t in self.ALLOWED_VIDEO_TYPES.split(",")]

    @property
    def allowed_maintenance_ips_list(self) -> List[str]:
        return [ip.strip() for ip in self.MAINTENANCE_ALLOWED_IPS.split(",")]

    @property
    def media_root_path(self) -> Path:
        return Path(self.MEDIA_ROOT)

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


settings = Settings()
