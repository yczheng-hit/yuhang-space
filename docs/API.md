# API 接口文档

## 基础信息

- 基础路径: `/api/v1`
- 认证方式: Bearer Token（JWT）
- 响应格式: JSON

## 认证接口

### POST /auth/register
用户注册。

**请求体:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string"
}
```

**响应:** `200` UserResponse

### POST /auth/login
用户登录（支持用户名或邮箱）。

**请求体:**
```json
{
  "username": "string",
  "password": "string"
}
```

**响应:** `200` TokenResponse

### POST /auth/refresh
刷新 Access Token。

**请求体:**
```json
{
  "refresh_token": "string"
}
```

**响应:** `200` { access_token, token_type }

## 日程接口

### GET /schedules
列出当前用户的所有日程。

**查询参数:** skip (int), limit (int)

### POST /schedules
创建日程。

### GET /schedules/{id}
获取单个日程。

### PATCH /schedules/{id}
更新日程。

### DELETE /schedules/{id}
删除日程。

### POST /schedules/{id}/media
为日程上传媒体文件（multipart/form-data）。

### GET /schedules/{id}/media
列出日程的所有媒体文件。

## 菜谱接口

### GET /recipes
列出当前用户的所有菜谱。

### POST /recipes
创建菜谱。

### GET /recipes/{id}
获取单个菜谱。

### PATCH /recipes/{id}
更新菜谱。

### DELETE /recipes/{id}
删除菜谱。

### POST /recipes/{id}/media
为菜谱上传媒体文件。

### GET /recipes/{id}/media
列出菜谱的所有媒体文件。

## LLM 接口

### POST /llm/chat
通用对话（流式 SSE 响应）。

### POST /llm/generate-schedule
通过 LLM 生成日程数据（不自动保存）。

### POST /llm/generate-recipe
通过 LLM 生成菜谱数据（不自动保存）。

## 运维接口

需要 HMAC 签名认证，仅限内部调用。

### GET /maintenance/health
健康检查。

### GET /maintenance/stats
数据库统计。

### POST /maintenance/cleanup-orphaned-media
清理孤立媒体文件。
