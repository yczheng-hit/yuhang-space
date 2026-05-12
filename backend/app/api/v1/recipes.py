"""菜谱路由 — CRUD + 媒体上传。"""

import uuid

from fastapi import APIRouter, File, UploadFile

from app.dependencies import CurrentUser, DBSession
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate
from app.services import media_service, recipe_service

router = APIRouter()


@router.post("", response_model=RecipeResponse)
async def create(data: RecipeCreate, db: DBSession, user: CurrentUser):
    """创建菜谱。"""
    recipe = await recipe_service.create_recipe(db, user.id, data)
    return recipe


@router.get("", response_model=list[RecipeResponse])
async def list_all(
    db: DBSession,
    user: CurrentUser,
    skip: int = 0,
    limit: int = 50,
):
    """列出当前用户的所有菜谱。"""
    return await recipe_service.list_recipes(db, user.id, skip, limit)


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_one(recipe_id: uuid.UUID, db: DBSession, user: CurrentUser):
    """获取单个菜谱。"""
    return await recipe_service.get_recipe(db, recipe_id, user.id)


@router.patch("/{recipe_id}", response_model=RecipeResponse)
async def update(
    recipe_id: uuid.UUID,
    data: RecipeUpdate,
    db: DBSession,
    user: CurrentUser,
):
    """更新菜谱。"""
    return await recipe_service.update_recipe(db, recipe_id, user.id, data)


@router.delete("/{recipe_id}")
async def delete(recipe_id: uuid.UUID, db: DBSession, user: CurrentUser):
    """删除菜谱。"""
    await recipe_service.delete_recipe(db, recipe_id, user.id)
    return {"detail": "已删除"}


@router.post("/{recipe_id}/media")
async def upload_media(
    recipe_id: uuid.UUID,
    file: UploadFile = File(...),
    db: DBSession = None,
    user: CurrentUser = None,
):
    """为菜谱上传媒体文件。"""
    media = await media_service.upload_media(db, user.id, file, recipe_id=recipe_id)
    return {"id": media.id, "file_path": media.file_path, "file_type": media.file_type}


@router.get("/{recipe_id}/media")
async def list_media(recipe_id: uuid.UUID, db: DBSession, user: CurrentUser):
    """列出菜谱的所有媒体文件。"""
    return await media_service.get_media_by_recipe(db, recipe_id)


@router.delete("/{recipe_id}/media/{media_id}")
async def delete_media(recipe_id: uuid.UUID, media_id: uuid.UUID, db: DBSession, user: CurrentUser):
    """删除媒体文件。"""
    await media_service.delete_media(db, media_id, user.id)
    return {"detail": "已删除"}
