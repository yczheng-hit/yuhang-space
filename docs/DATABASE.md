# 数据库 Schema 文档

## ER 关系图

```
users (1) ──→ (N) schedules
users (1) ──→ (N) recipes
users (1) ──→ (N) media_files
schedules (1) ──→ (N) media_files
recipes (1) ──→ (N) media_files
```

## 表结构

### users（用户表）

| 字段 | 类型 | 约束 |
|------|------|------|
| id | UUID | PK |
| username | VARCHAR(50) | UNIQUE, NOT NULL, INDEX |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX |
| hashed_password | VARCHAR(255) | NOT NULL |
| is_active | BOOLEAN | NOT NULL, DEFAULT true |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

### schedules（日程表）

| 字段 | 类型 | 约束 |
|------|------|------|
| id | UUID | PK |
| user_id | UUID | FK → users.id, INDEX |
| title | VARCHAR(200) | NOT NULL |
| description | TEXT | NULLABLE |
| start_time | TIMESTAMPTZ | NOT NULL |
| end_time | TIMESTAMPTZ | NULLABLE |
| priority | SMALLINT | NOT NULL, DEFAULT 0 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' |
| recurrence_rule | VARCHAR(100) | NULLABLE |
| tags | JSONB | DEFAULT '[]' |
| ai_generated | BOOLEAN | NOT NULL, DEFAULT false |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

### recipes（菜谱表）

| 字段 | 类型 | 约束 |
|------|------|------|
| id | UUID | PK |
| user_id | UUID | FK → users.id, INDEX |
| title | VARCHAR(200) | NOT NULL |
| description | TEXT | NULLABLE |
| ingredients | JSONB | NOT NULL, DEFAULT '[]' |
| instructions | JSONB | NOT NULL, DEFAULT '[]' |
| prep_time_min | INTEGER | NULLABLE |
| cook_time_min | INTEGER | NULLABLE |
| servings | INTEGER | NULLABLE |
| tags | JSONB | DEFAULT '[]' |
| ai_generated | BOOLEAN | NOT NULL, DEFAULT false |
| created_at | TIMESTAMPTZ | NOT NULL |
| updated_at | TIMESTAMPTZ | NOT NULL |

### media_files（媒体文件表）

| 字段 | 类型 | 约束 |
|------|------|------|
| id | UUID | PK |
| owner_id | UUID | FK → users.id, INDEX |
| schedule_id | UUID | FK → schedules.id, NULLABLE |
| recipe_id | UUID | FK → recipes.id, NULLABLE |
| file_type | VARCHAR(10) | NOT NULL |
| file_path | TEXT | NOT NULL |
| mime_type | VARCHAR(100) | NOT NULL |
| file_size_bytes | BIGINT | NOT NULL |
| original_name | VARCHAR(255) | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL |

**约束:** CHECK ((schedule_id IS NOT NULL) OR (recipe_id IS NOT NULL))

## 密码规则

- 最少 6 位
- 必须包含至少一个英文字母和一个数字
- 使用 bcrypt 哈希存储
