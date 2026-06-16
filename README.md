# Learning Growth System

基于 **Python + FastAPI + React + MySQL + Redis Vector** 的通用学习成长系统。

系统支持多目标管理、用户画像、目标绑定知识库、基于私有知识库的 RAG 问答、任务日历、AI 任务优化与补充、任务计时和每日复盘。考研只是可配置的 `goal_type` 或 `domain` 之一，不再是系统唯一场景。

## Core Capabilities

- 用户画像：记录学习阶段、能力水平、偏好和约束。
- 目标管理：支持学习、考试、项目、论文、职业成长等多种目标。
- 知识库：每个目标可以绑定一个或多个知识库。
- 文档处理：支持上传 txt、md、pdf、json，生成 chunk 并落 MySQL。
- Redis Vector：只保存向量索引和检索 metadata，可信完整内容保留在 MySQL。
- RAG 问答：只依据检索 context 回答，返回 sources、hit_source 和 retrieval_debug。
- 任务日历：按日期管理任务，支持 AI 优化、AI 补充、状态管理和计时。
- 每日复盘：记录完成率、实际用时、问题和调整建议。

## Backend Environment

复制并修改配置：

```bash
cp backend/.env.example backend/.env
```

关键配置：

```env
PROJECT_NAME=learning-growth-system
MYSQL_DATABASE=learning_growth
REDIS_VECTOR_INDEX_NAME=idx:learning:chunks
REDIS_VECTOR_KEY_PREFIX=learning:chunk
AUTO_CREATE_TABLES=false
```

不要把 API Key 或数据库密码写死到代码中。

## Reset Database

本次重构不兼容旧业务数据，推荐重置数据库：

```bash
docker compose down -v
docker compose up -d mysql redis
cd backend
alembic upgrade head
cd ..
docker compose up --build
```

如 Redis 中仍有历史向量索引，请在 Redis Insight 或 `redis-cli FT._LIST` 中确认旧索引名后删除，再重新向量化。新索引会按 `idx:learning:chunks` 自动创建。

## Main APIs

### Profiles

- `GET /api/v1/profiles/me`
- `PUT /api/v1/profiles/me`
- `POST /api/v1/profiles/onboarding`

### Goals

- `GET /api/v1/goals`
- `POST /api/v1/goals`
- `GET /api/v1/goals/{goal_id}`
- `PATCH /api/v1/goals/{goal_id}`
- `DELETE /api/v1/goals/{goal_id}`
- `POST /api/v1/goals/{goal_id}/activate`

### Knowledge Bases

- `GET /api/v1/knowledge-bases`
- `POST /api/v1/knowledge-bases`
- `GET /api/v1/knowledge-bases/{kb_id}`
- `PATCH /api/v1/knowledge-bases/{kb_id}`
- `DELETE /api/v1/knowledge-bases/{kb_id}`
- `POST /api/v1/knowledge-bases/{kb_id}/bind-goal/{goal_id}`

### Documents

上传文档：

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@notes.md" \
  -F "knowledge_base_id=1" \
  -F "goal_id=1" \
  -F "domain=software" \
  -F "category=backend" \
  -F "tags=fastapi,rag"
```

文档列表支持 `knowledge_base_id`、`goal_id`、`domain`、`category` 过滤。

### RAG

向量化：

```bash
curl -X POST http://localhost:8000/api/v1/rag/index \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"knowledge_base_id":1,"limit":100,"batch_size":32}'
```

问答：

```bash
curl -X POST http://localhost:8000/api/v1/rag/ask \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"question":"这份资料里推荐的实践步骤是什么？","knowledge_base_id":1,"top_k":5}'
```

无检索结果时，后端直接返回“当前知识库没有找到可靠依据”，不会调用 LLM。

### Tasks

创建日期任务：

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"content":"完成 FastAPI 依赖注入笔记整理","goal_id":1,"category":"backend","planned_date":"2026-06-16","estimated_minutes":60,"priority":"high"}'
```

计时：

- `POST /api/v1/tasks/{task_id}/start`
- `POST /api/v1/tasks/{task_id}/pause`
- `POST /api/v1/tasks/{task_id}/complete`

AI：

- `POST /api/v1/tasks/ai/optimize`
- `POST /api/v1/tasks/ai/supplement`

AI 补充只基于用户任务历史、当天已有任务、可用时间和反馈，不调用 RAG 或 Redis Vector。

### Reviews

- `GET /api/v1/reviews`
- `POST /api/v1/reviews`
- `PATCH /api/v1/reviews/{review_id}`
- `GET /api/v1/reviews/stats?goal_id=1`

## Database Tables

- `users`：认证用户。
- `user_profiles`：用户画像。
- `goals`：学习或成长目标。
- `knowledge_bases`：目标绑定的知识库。
- `documents`：文档元数据。
- `document_chunks`：文档切片与来源 metadata。
- `rag_query_logs`：RAG 问答日志。
- `task_items`：用户任务。
- `task_execution_sessions`：任务计时会话。
- `daily_reviews`：每日复盘。

## Verification

后端：

```bash
cd backend
alembic upgrade head
python -m pytest
```

前端：

```bash
cd frontend
npm run build
```

访问：

- OpenAPI: http://localhost:8000/docs
- Frontend: http://localhost:5173
