"""LLM 相关 Pydantic 模型。"""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class GenerateScheduleRequest(BaseModel):
    prompt: str


class GenerateRecipeRequest(BaseModel):
    prompt: str
