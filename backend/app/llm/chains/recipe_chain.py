"""菜谱生成 Chain。"""

from langchain_core.output_parsers import StrOutputParser

from app.llm.client import get_llm_client
from app.llm.prompts.recipe_prompt import RECIPE_GENERATION_PROMPT


def get_recipe_chain():
    """返回菜谱生成链（Prompt | LLM | OutputParser）。"""
    llm = get_llm_client()
    return RECIPE_GENERATION_PROMPT | llm | StrOutputParser()


async def generate_recipe(user_input: str) -> str:
    """调用 LLM 生成菜谱数据（返回 JSON 字符串）。"""
    chain = get_recipe_chain()
    return await chain.ainvoke({"user_input": user_input})
