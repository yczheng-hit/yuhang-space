"""pathlib 文件工具与通用校验器。"""

import re
from pathlib import Path
from uuid import uuid4

from app.core.constants import FILE_TYPE_IMAGE, FILE_TYPE_VIDEO


def sanitize_filename(filename: str) -> str:
    """清洗文件名：去除路径分隔符和特殊字符。"""
    name = Path(filename).name
    name = re.sub(r"[^\w.\-]", "_", name)
    return name[:200]


def build_upload_path(
    media_root: Path,
    user_id: str,
    file_type: str,
    original_filename: str,
) -> Path:
    """构建上传文件的完整路径（pathlib）。

    结构: {MEDIA_ROOT}/{user_id}/{file_type}/{year}/{month}/{uuid}_{sanitized_name}
    """
    from datetime import datetime

    now = datetime.now()
    safe_name = sanitize_filename(original_filename)
    unique_name = f"{uuid4().hex}_{safe_name}"

    return media_root / user_id / file_type / str(now.year) / f"{now.month:02d}" / unique_name


def classify_file_type(mime_type: str) -> str:
    """根据 MIME 类型分类为 image 或 video。"""
    if mime_type.startswith("image/"):
        return FILE_TYPE_IMAGE
    if mime_type.startswith("video/"):
        return FILE_TYPE_VIDEO
    raise ValueError(f"不支持的文件类型: {mime_type}")


def is_allowed_extension(filename: str, allowed_types: list[str]) -> bool:
    """检查文件扩展名是否在允许列表中。"""
    ext = Path(filename).suffix.lstrip(".").lower()
    return ext in allowed_types
