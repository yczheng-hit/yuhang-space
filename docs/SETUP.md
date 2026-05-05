# 开发环境搭建指南

## 前置要求

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+（或使用 Docker）

## Windows 开发环境

### 1. 克隆仓库

```bash
git clone <repo-url> D:\yuhang-space
cd D:\yuhang-space
```

### 2. 后端环境

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # PowerShell
pip install -e ".[dev]"
```

### 3. 配置环境变量

```bash
copy ..\.env.example ..\.env
# 编辑 .env 填入实际值（数据库连接、JWT 密钥、LLM API Key 等）
```

### 4. 启动数据库

使用 Docker 快速启动 PostgreSQL：

```bash
docker run -d --name yuhang-db -e POSTGRES_USER=yuhang -e POSTGRES_PASSWORD=password -e POSTGRES_DB=yuhang_space -p 5432:5432 postgres:16-alpine
```

或手动安装 PostgreSQL 并创建数据库。

### 5. 运行数据库迁移

```bash
cd backend
alembic upgrade head
```

### 6. 启动后端

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`，API 请求自动代理到后端。

## Linux 开发环境

```bash
# 后端
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 前端
cd frontend
npm install
npm run dev
```

## 代码检查

```bash
# 后端
cd backend
ruff check app/
ruff format app/
mypy app/

# 前端
cd frontend
npm run lint
```
