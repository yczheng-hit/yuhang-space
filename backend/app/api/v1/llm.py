"""LLM 路由 — 对话、日程生成、菜谱生成。"""

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.config import settings
from app.dependencies import CurrentUser
from app.schemas.llm import ChatRequest, GenerateRecipeRequest, GenerateScheduleRequest

router = APIRouter()


def _check_llm_enabled():
    """检查 LLM 是否启用。"""
    if not settings.LLM_ENABLED or not settings.LLM_API_KEY:
        raise HTTPException(status_code=503, detail="LLM 功能未启用或 API Key 未配置")


@router.post("/chat")
async def chat(req: ChatRequest, user: CurrentUser):
    """通用对话（流式响应）。"""
    _check_llm_enabled()

    from app.llm.client import get_llm_client

    llm = get_llm_client()

    async def generate():
        async for chunk in llm.astream(req.message):
            yield f"data: {json.dumps({'content': chunk.content}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.post("/generate-schedule")
async def generate_schedule(req: GenerateScheduleRequest, user: CurrentUser):
    """通过 LLM 生成日程数据（不自动保存）。"""
    _check_llm_enabled()

    from app.llm.chains.schedule_chain import generate_schedule

    result = await generate_schedule(req.prompt)
    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        data = {"raw_response": result}
    return data


@router.post("/generate-recipe")
async def generate_recipe(req: GenerateRecipeRequest, user: CurrentUser):
    """通过 LLM 生成菜谱数据（不自动保存）。"""
    _check_llm_enabled()

    from app.llm.chains.recipe_chain import generate_recipe

    result = await generate_recipe(req.prompt)
    try:
        data = json.loads(result)
    except json.JSONDecodeError:
        data = {"raw_response": result}
    return data
