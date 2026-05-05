# 寰宇智杭 (yuhang-space) — AI 协作指南

## 项目概述
智能生活管理平台：日程管理 + 多媒体存储 + 菜谱管理 + 大模型辅助。

## 技术栈
- **后端**: Python 3.12 + FastAPI + LangChain + SQLAlchemy (async) + PostgreSQL
- **前端**: Vue 3 + Vite + TailwindCSS v4 + Pinia + Axios
- **部署**: Linux 原生 (Nginx + systemd)

## 严格规范
- 所有文件路径操作**必须**使用 `pathlib`，严禁硬编码斜杠拼接
- 敏感信息**必须**通过 `.env` 管理，提供 `.env.example`，绝不硬编码
- 代码分层严格：Router → Service → Model，不跨层调用
- 为关键函数添加 Docstring（中文或英文均可）
- 使用 `ruff` 格式化，`mypy` 类型检查

## 项目结构
```
backend/app/
  api/v1/      — 路由层（HTTP 关注点）
  schemas/     — Pydantic 请求/响应模型
  models/      — SQLAlchemy ORM 模型
  services/    — 业务逻辑
  llm/         — LangChain 集成（client + chains + prompts）
  security/    — 认证与加密工具
  core/        — 异常、常量、工具函数
frontend/src/
  api/         — Axios HTTP 客户端
  components/  — 可复用 UI 组件
  views/       — 页面级组件
  stores/      — Pinia 状态管理
  composables/ — 组合函数
```

## 常用命令
```bash
# 后端
cd backend && pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
alembic upgrade head
ruff check app/
mypy app/

# 前端
cd frontend && npm install
npm run dev
npm run build
```

## LLM 集成
- 使用 LangChain + OpenAI 兼容协议（`base_url` 参数切换供应商）
- 配置项：`LLM_ENABLED`、`LLM_API_KEY`、`LLM_BASE_URL`、`LLM_MODEL_NAME`
- LLM 是增强层，非依赖项 — 未配置时返回 503
