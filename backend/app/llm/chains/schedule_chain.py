"""日程生成 Chain。"""

from langchain_core.output_parsers import StrOutputParser

from app.llm.client import get_llm_client
from app.llm.prompts.schedule_prompt import SCHEDULE_GENERATION_PROMPT


def get_schedule_chain():
    """返回日程生成链（Prompt | LLM | OutputParser）。"""
    llm = get_llm_client()
    return SCHEDULE_GENERATION_PROMPT | llm | StrOutputParser()


async def generate_schedule(user_input: str) -> str:
    """调用 LLM 生成日程数据（返回 JSON 字符串）。"""
    chain = get_schedule_chain()
    return await chain.ainvoke({"user_input": user_input})
