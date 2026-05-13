"""媒体文件业务逻辑。"""

import uuid

import aiofiles
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.constants import FILE_TYPE_IMAGE, FILE_TYPE_VIDEO
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.utils import build_upload_path, classify_file_type, is_allowed_extension
from app.models.media import MediaFile


async def upload_media(
    db: AsyncSession,
    user_id: uuid.UUID,
    file: UploadFile,
    schedule_id: uuid.UUID | None = None,
    recipe_id: uuid.UUID | None = None,
    media_type: str | None = None,
) -> MediaFile:
    """上传并保存媒体文件。"""
    if not file.content_type:
        raise BadRequestException("无法识别文件类型")

    # 校验文件类型
    file_type = classify_file_type(file.content_type)
    if file_type == FILE_TYPE_IMAGE and not is_allowed_extension(
        file.filename or "", settings.allowed_image_types_list
    ):
        raise BadRequestException("不支持的图片格式")
    if file_type == FILE_TYPE_VIDEO and not is_allowed_extension(
        file.filename or "", settings.allowed_video_types_list
    ):
        raise BadRequestException("不支持的视频格式")

    # 读取文件内容并校验大小
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise BadRequestException(f"文件大小超过限制 ({settings.MAX_UPLOAD_SIZE_MB}MB)")

    # 构建存储路径并写入
    file_path = build_upload_path(
        settings.media_root_path,
        str(user_id),
        file_type,
        file.filename or "unknown",
    )
    file_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # 创建数据库记录
    relative_path = str(file_path.relative_to(settings.media_root_path))
    media = MediaFile(
        owner_id=user_id,
        schedule_id=schedule_id,
        recipe_id=recipe_id,
        file_type=file_type,
        file_path=relative_path,
        mime_type=file.content_type,
        file_size_bytes=len(content),
        original_name=file.filename or "unknown",
        media_type=media_type,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media


async def get_media_by_schedule(
    db: AsyncSession, schedule_id: uuid.UUID
) -> list[MediaFile]:
    """获取日程关联的所有媒体文件。"""
    result = await db.execute(
        select(MediaFile).where(MediaFile.schedule_id == schedule_id)
    )
    return list(result.scalars().all())


async def get_media_by_recipe(
    db: AsyncSession, recipe_id: uuid.UUID
) -> list[MediaFile]:
    """获取菜谱关联的所有媒体文件。"""
    result = await db.execute(
        select(MediaFile).where(MediaFile.recipe_id == recipe_id)
    )
    return list(result.scalars().all())


async def delete_media(
    db: AsyncSession, media_id: uuid.UUID, user_id: uuid.UUID
) -> None:
    """删除媒体文件（数据库记录 + 磁盘文件）。"""
    result = await db.execute(
        select(MediaFile).where(
            MediaFile.id == media_id, MediaFile.owner_id == user_id
        )
    )
    media = result.scalar_one_or_none()
    if media is None:
        raise NotFoundException("媒体文件不存在")

    # 删除磁盘文件
    full_path = settings.media_root_path / media.file_path
    if full_path.exists():
        full_path.unlink()

    await db.delete(media)
    await db.commit()
