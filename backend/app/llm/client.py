"""LangChain LLM 客户端 — 从 .env 配置 ChatOpenAI。"""

from langchain_openai import ChatOpenAI

from app.config import settings


def get_llm_client() -> ChatOpenAI:
    """返回配置好的 ChatOpenAI 实例。

    通过 base_url 参数实现 OpenAI 兼容协议，切换供应商只需修改 .env。
    """
    if not settings.LLM_ENABLED or not settings.LLM_API_KEY:
        raise RuntimeError("LLM 未启用或 API Key 未配置")

    return ChatOpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        model=settings.LLM_MODEL_NAME,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
        streaming=True,
    )
