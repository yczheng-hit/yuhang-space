# 寰宇智杭 (yuhang-space)

> 一个用 AI 辅助开发的智能生活管理平台

## 这是什么？

一个集生活日记、菜谱收藏、多媒体管理、AI 对话于一体的个人生活助手。用现代 Web 技术栈搭建，支持图片/视频上传，内置大模型能力。

## 功能

- 用户注册/登录（用户名 + 密码）
- 生活日记（emoji 心情、标签、图片/视频附件，支持列表/时间线/日历三种视图）
- 菜谱库（食材、步骤、标签、图片/视频）
- 多媒体上传与回放（图片预览、视频播放）
- 编辑已提交的内容
- AI 对话（流式响应）
- AI 生成日记/菜谱
- 运维 API（HMAC 签名认证）

## 技术栈

**后端**
- Python 3.12 + FastAPI (≥0.115)
- SQLAlchemy 2.0 (async) + SQLite (aiosqlite)
- LangChain (≥0.3) + OpenAI 兼容协议
- JWT 认证 (PyJWT ≥2.9) + bcrypt 密码哈希
- Pydantic v2 (≥2.9) + pydantic-settings (≥2.6)

**前端**
- Vue 3 (≥3.5) + Vite (≥6.2)
- TailwindCSS v4 (≥4.0) + @tailwindcss/vite
- Pinia (≥2.3) 状态管理
- Axios (≥1.7) HTTP 客户端
- vue-router (≥4.5)

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 18+

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 配置环境变量
cp ../.env.example ../.env
# 编辑 .env 填入 JWT 密钥等配置（数据库默认 SQLite，无需额外配置）

# 初始化数据库
python -m alembic upgrade head

# 启动
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 前端

```bash
cd frontend
npm install
npx vite build
```

访问 http://localhost:8080

## 配置说明

复制 `.env.example` 为 `.env` 后按需修改：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | 数据库连接 | `sqlite+aiosqlite:///./yuhang_space.db` |
| `JWT_SECRET_KEY` | JWT 签名密钥 | 需手动设置 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access Token 过期时间 | 30 |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh Token 过期时间 | 7 |
| `LLM_ENABLED` | 启用大模型 | true |
| `LLM_API_KEY` | 大模型 API Key | - |
| `LLM_BASE_URL` | 大模型接口地址 | OpenAI |
| `LLM_MODEL_NAME` | 模型名称 | gpt-4o-mini |
| `MEDIA_ROOT` | 媒体文件存储目录 | `./media` |
| `MAX_UPLOAD_SIZE_MB` | 最大上传大小 | 50 |
| `BACKEND_PORT` | 后端端口 | 8080 |
| `CORS_ORIGINS` | CORS 允许来源 | localhost:8080 |

## 生产部署

后端直接服务前端 dist + API + 媒体文件，统一端口 8080。

```bash
# 构建前端
cd frontend && npm run build

# 启动（后端同时服务前端静态文件）
cd backend && .venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

访问 http://your-server:8080

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
  tests/         → pytest 单元测试 (44 个用例)
frontend/
  src/
    api/         → HTTP 客户端
    components/  → UI 组件（含表单弹窗、媒体上传/展示）
    views/       → 页面
    stores/      → Pinia 状态
  dist/          → 前端构建产物（由后端 SPA 服务提供）
tests/
  web_test.py    → E2E 测试 (71 个用例)
```

## API 文档

启动后端后访问 http://localhost:8080/docs 查看 Swagger 文档。

详细 API 文档见 [docs/API.md](docs/API.md)

## 许可

MIT