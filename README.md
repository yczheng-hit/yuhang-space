# 寰宇智杭 (yuhang-space)

> 一个用 AI 辅助开发的智能生活管理平台

## 这是什么？

一个集生活日记、菜谱收藏、多媒体管理、AI 对话于一体的个人生活助手。用现代 Web 技术栈搭建，支持图片/视频上传，内置大模型能力。

## 功能

- 用户注册/登录（用户名 + 密码）
- 生活日记（emoji 心情、标签、图片/视频附件）
- 菜谱库（食材、步骤、标签、图片/视频）
- 多媒体上传与回放（图片预览、视频播放）
- 编辑已提交的内容
- AI 对话（流式响应）
- AI 生成日记/菜谱
- 运维 API（HMAC 签名认证）

## 技术栈

**后端**
- Python 3.12 + FastAPI
- SQLAlchemy (async) + SQLite (aiosqlite)
- LangChain + OpenAI 兼容协议
- JWT 认证 + bcrypt 密码哈希

**前端**
- Vue 3 + Vite
- TailwindCSS v4
- Pinia 状态管理
- Axios HTTP 客户端

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy aiosqlite alembic pyjwt bcrypt pydantic pydantic-settings langchain langchain-openai httpx python-dotenv aiofiles

# 配置环境变量
cp ../.env.example ../.env
# 编辑 .env 填入 JWT 密钥等配置（数据库默认 SQLite，无需额外配置）

# 初始化数据库
cd backend
python -m alembic upgrade head

# 启动
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5174

## 项目结构

```
backend/
  app/
    api/v1/      → 路由层
    schemas/     → Pydantic 模型
    models/      → SQLAlchemy ORM
    services/    → 业务逻辑
    llm/         → LangChain 集成
    security/    → 认证工具
    core/        → 通用工具
  alembic/       → 数据库迁移
frontend/
  src/
    api/         → HTTP 客户端
    components/  → UI 组件（含表单弹窗、媒体上传/展示）
    views/       → 页面
    stores/      → Pinia 状态
```

## API 文档

启动后端后访问 http://localhost:8000/docs 查看 Swagger 文档。

## 许可

MIT
