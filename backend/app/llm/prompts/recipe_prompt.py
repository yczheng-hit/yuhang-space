"""菜谱生成提示词模板。"""

from langchain_core.prompts import ChatPromptTemplate

RECIPE_GENERATION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "你是一个专业的厨师助手。用户会描述想要的菜品或食材，"
        "你需要生成一份完整的菜谱。\n"
        "请返回 JSON 格式，包含以下字段：\n"
        "- title: 菜谱名称\n"
        "- description: 简要描述\n"
        "- ingredients: 食材数组，每项包含 name、amount、unit\n"
        "- instructions: 步骤数组（有序字符串列表）\n"
        "- prep_time_min: 准备时间（分钟）\n"
        "- cook_time_min: 烹饪时间（分钟）\n"
        "- servings: 份数\n"
        "- tags: 标签数组（如素食、快手菜等）",
    ),
    ("human", "{user_input}"),
])
