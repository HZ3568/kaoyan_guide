# kaoyan-guide

基于 **Python + FastAPI + React + MySQL + Redis Vector** 的考研院校信息 RAG 查询与 AI 学习任务日历系统。

## 当前包含

- FastAPI 后端项目结构
- React + Vite + TypeScript 前端项目结构
- MySQL / Redis Stack docker-compose
- `/health`、`/health/db`、`/health/redis` 基础健康检查
- JWT 鉴权基础代码
- TXT / Markdown / CSV / PDF / OCR JSON 文档上传、解析、chunk 入库流程
- OCR JSON 表格按“院校-专业-科目-分数线”等语义生成 table chunk，并落库 OCR 结构化记录
- Word / 图片等暂未解析格式会标记为 `unsupported`，不会写入占位 chunk
- Embedding 抽象接口与 Redis Vector chunk 索引、TopK 检索接口
- RAG Ask 问答链路：向量检索、提示词构建、LLM 调用、来源返回、查询日志入库
- AI 学习任务日历链路：用户按日期管理任务，AI 支持任务表述优化、任务拆分建议、基于历史完成情况的当天任务补充、执行反馈和轻量调整

## 后端启动

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

访问：<http://localhost:8000/docs>

本地后端连接 Docker MySQL 时，`.env.example` 默认使用 `MYSQL_PORT=3307`。
如需生产或共享环境，请复制 `.env.example` 为 `.env` 并修改数据库密码、`SECRET_KEY` 等配置，不要把真实密钥提交到仓库。

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问：<http://localhost:5173>

## Docker 启动 MySQL / Redis / Backend

```bash
docker compose up -d --build
```

Docker Compose 默认读取 `backend/.env`。首次运行前请复制 `backend/.env.example` 为 `backend/.env`，并在容器内把后端 MySQL 地址覆盖为 `mysql:3306`。

启动后访问：<http://localhost:8000/docs>

健康检查：

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/db
curl http://localhost:8000/health/redis
```

## 文档导入与切片

当前支持格式：

- `.txt`
- `.md` / `.markdown`
- `.csv`（按普通文本切片，保留旧能力）
- `.pdf`（依赖 `pypdf` 提取文本）
- OCR 后的 `.json`

API 上传示例：

```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@./data/raw/math.md" \
  -F "source=本地资料库" \
  -F "subject=数学" \
  -F "tags=高数,真题"
```

本地目录批量导入示例。`path` 必须位于 `LOCAL_IMPORT_ROOT` 下，Docker Compose 中默认是 `/app/data`，对应宿主机 `./data`：

```bash
curl -X POST http://localhost:8000/api/v1/documents/import-local \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"path":"raw","recursive":true,"source":"本地资料库","subject":"数学","tags":["高数","真题"]}'
```

命令行批量导入：

```bash
cd backend
python -m app.ingestion.cli raw --user-id 1 --source 本地资料库 --subject 数学 --tag 高数
```

查询文档与 chunks：

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/documents
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/documents/<document_id>/chunks
```

数据库验证：

```sql
SELECT id, title, file_type, source_type, parse_status FROM documents ORDER BY id DESC LIMIT 5;
SELECT document_id, chunk_index, chunk_type, page_number, token_count FROM document_chunks ORDER BY id DESC LIMIT 10;
SELECT document_id, school, major, exam_subjects, score_line FROM ocr_table_records ORDER BY id DESC LIMIT 10;
```

## Embedding 与 Redis Vector 检索

环境变量：

```bash
LLM_PROVIDER=mock
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL=gpt-4o-mini
LLM_TIMEOUT_SECONDS=60
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=1200
EMBEDDING_PROVIDER=mock
EMBEDDING_API_KEY=
EMBEDDING_BASE_URL=
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
EMBEDDING_BATCH_SIZE=32
EMBEDDING_TIMEOUT_SECONDS=30
REDIS_VECTOR_INDEX_NAME=idx:kaoyan:chunks
REDIS_VECTOR_KEY_PREFIX=rag:chunk
REDIS_VECTOR_DISTANCE_METRIC=COSINE
```

`EMBEDDING_PROVIDER=mock` 用于本地跑通流程，不代表真实语义效果。切换 OpenAI 或兼容接口时使用：

```bash
LLM_PROVIDER=openai
LLM_API_KEY=<your-api-key>
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
EMBEDDING_PROVIDER=openai
EMBEDDING_API_KEY=<your-api-key>
EMBEDDING_BASE_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
```

Redis 索引结构：

- Index：`idx:kaoyan:chunks`
- Key：`rag:chunk:<chunk_id>`
- Vector 字段：`embedding`，`FLOAT32`，`HNSW`，维度来自 `EMBEDDING_DIM`
- 过滤字段：`chunk_id`、`document_id`、`user_id`、`subject`、`school`、`major`、`exam_year`、`chunk_type`
- 展示字段：`content_preview`、`source`、`metadata`
- MySQL 的 `document_chunks.content` 仍是可信完整内容，Redis 只保存向量索引和检索辅助字段。

为当前用户的未向量化 chunk 建立索引：

```bash
curl -X POST http://localhost:8000/api/v1/rag/index \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"limit":100,"batch_size":32}'
```

查询索引状态：

```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/rag/index/status
```

向量检索示例：

```bash
curl -X POST http://localhost:8000/api/v1/rag/search \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"query":"计算机专业 408 分数线是多少？","top_k":5,"filters":{"subject":"计算机"}}'
```

清空并重建索引：

```bash
docker compose exec redis redis-cli FT.DROPINDEX idx:kaoyan:chunks DD
docker compose exec mysql sh -lc \
  'mysql -h localhost -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -D "$MYSQL_DATABASE" -e "UPDATE document_chunks SET is_vectorized=0, embedding_status='"'"'pending'"'"', vector_index_key=NULL;"'
curl -X POST http://localhost:8000/api/v1/rag/index \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"limit":1000,"batch_size":32,"force_reindex":true}'
```

## RAG 问答

问答接口：

```bash
curl -X POST http://localhost:8000/api/v1/rag/ask \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"question":"北京大学计算机专业分数线是多少？","top_k":5,"filters":{"subject":"计算机"},"stream":false}'
```

返回示例：

```json
{
  "answer": "根据当前知识库资料，北京大学计算机科学与技术复试线为 350。[来源1]",
  "sources": [
    {
      "chunk_id": 11,
      "document_id": 7,
      "score": 0.91,
      "title": "北京大学计算机招生目录",
      "source": "OCR招生目录",
      "source_type": "uploaded",
      "source_url": null,
      "file_name": "ocr.json",
      "page_number": 1,
      "location": {"position_start": null, "position_end": null},
      "content_preview": "院校：北京大学\n专业：计算机科学与技术\n分数线：350",
      "metadata": {"subject": "计算机"}
    }
  ],
  "hit_source": true,
  "model_provider": "mock",
  "model_name": "gpt-4o-mini",
  "log_id": 23,
  "retrieval_debug": {"top_k": 5, "retrieved": 1, "mode": "vector_rag", "stream": false}
}
```

如果没有检索到来源，接口直接返回：

```json
{
  "answer": "当前知识库没有找到依据。请先上传并向量化相关资料，或调整问题和筛选条件。",
  "sources": [],
  "hit_source": false
}
```

日志写入：

- 每次 `/api/v1/rag/ask` 都会写入 `rag_query_logs`。
- `question` 记录用户问题。
- `filters_json` 记录筛选条件。
- `retrieved_chunks_json` 记录命中的 chunk、分数、来源、位置和内容预览。
- `model_provider`、`model_name`、`model_answer` 记录模型调用结果。
- `hit_source=false` 表示没有找到可引用来源。

反幻觉约束：

- 检索结果为空时不调用 LLM，直接说明“当前知识库没有找到依据”。
- 系统提示词要求只根据给定上下文回答。
- 涉及院校、专业、分数线、招生人数、考试科目时要求引用来源编号。
- 返回结构化 `sources`，前端可以展示 chunk 来源，MySQL 保留完整可信内容。

测试问题：

- `北京大学计算机专业分数线是多少？`
- `408 计算机专业课应该复习哪些科目？`
- `这个院校的人工智能方向招生人数是多少？`

## AI 学习任务日历

学习任务模块不再从 RAG 资料生成任务。RAG 只负责院校信息、专业信息、招生人数、分数线、考试科目、参考资料等知识库检索问答。任务模块围绕“按日期维护任务”展开，接口前缀为 `/api/v1/tasks`、`/api/v1/calendar-tasks`，兼容保留 `/api/v1/daily-plans` 的状态更新与反馈接口。

在指定日期创建任务：

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"完成高数极限专题 20 道选择题","description":"记录错题并总结 3 个易错点","category":"考研复习","subject":"数学","priority":"high","difficulty":"normal","estimated_minutes":90,"deadline":"2026-06-20","status":"pending","date":"2026-06-15","source_type":"manual"}'
```

按日期查询任务：

```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/calendar-tasks?date=2026-06-15"
```

月历统计：

```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/calendar-tasks/month?year=2026&month=6"
```

AI 优化用户输入任务。该接口只返回建议，不会保存正式任务：

```bash
curl -X POST http://localhost:8000/api/v1/tasks/ai/optimize \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"raw_title":"做数学题","raw_description":"","date":"2026-06-15","subject":"数学","estimated_minutes":90,"priority":"high"}'
```

AI 根据历史任务和当天已有任务补充建议。该接口不调用 RAG / Redis Vector，也不会直接创建正式任务：

```bash
curl -X POST http://localhost:8000/api/v1/calendar-tasks/ai/supplement \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-06-15","available_minutes":240,"max_new_tasks":3}'
```

用户采用 AI 建议后再创建正式任务：

```bash
curl -X POST http://localhost:8000/api/v1/calendar-tasks/accept-suggestion \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"整理今日学习复盘","description":"记录实际用时、阻塞点和下一步动作","category":"复盘","priority":"medium","estimated_minutes":30,"date":"2026-06-15","status":"pending","source_type":"ai_supplement","is_ai_generated":true}'
```

更新任务与状态：

```bash
curl -X PATCH http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"estimated_minutes":90,"priority":"urgent"}'

curl -X PATCH http://localhost:8000/api/v1/tasks/1/status \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"status":"completed"}'
```

提交反馈：

```bash
curl -X POST http://localhost:8000/api/v1/tasks/1/feedback \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"actual_minutes":85,"difficulty_feedback":"normal","completion_note":"节奏合适，但后续需要二刷"}'
```

生成边界：

- RAG 模块只负责知识库检索问答，继续保留 `sources`、`hit_source`、`retrieval_debug` 和无依据拒答。
- 学习任务模块只基于 MySQL 中的用户任务、日期安排、反馈和近期完成情况做任务日历管理。
- LLM 只负责任务表述优化、拆分建议、补充建议和自然语言原因说明；所有 AI 建议都需要用户确认后才会成为正式任务。
- Redis 只用于 RAG 向量检索，不参与学习任务补充。

## 数据库迁移

阶段 2 已接入 Alembic。首次创建或更新 MySQL 表结构：

```bash
cd backend
alembic upgrade head
```

如果没有复制 `.env`，可以临时指定 Compose 暴露的本地 MySQL：

```powershell
cd backend
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3307"
$env:MYSQL_USER="kaoyan_app"
$env:MYSQL_PASSWORD="change-this-dev-db-password"
$env:MYSQL_DATABASE="kaoyan_guide"
.\.venv\Scripts\python.exe -m alembic upgrade head
```

当前基础表覆盖：

- `documents` / `document_chunks`：文档元数据、切片、向量化状态和来源追踪字段。
- `ocr_tasks` / `ocr_table_records`：OCR 原始结果与院校专业表格结构化记录。
- `rag_query_logs`：RAG 问题、检索 chunk、模型回答和来源命中日志。
- `task_items`：用户任务表。
- `daily_plans` / `daily_plan_tasks`：按日期聚合的任务安排和日期内任务关联。
- `task_feedback` / `task_ai_suggestions`：任务反馈、AI 优化、拆分和补充建议。
- `chat_sessions` / `chat_messages`：问答会话和消息记录。

旧版 `learning_profiles` / `learning_plans` / `learning_tasks` 与长期规划强绑定的 `study_*`、`weekly_plans`、`daily_tasks` 表已经通过迁移移除；学习任务统一使用 `/api/v1/tasks`、`/api/v1/calendar-tasks` 和保留兼容的 `/api/v1/daily-plans` 状态/反馈接口。

## 测试

```bash
cd backend
.venv\Scripts\python -m pytest  # Windows
```

当前测试覆盖：

- 健康检查
- MySQL / Redis 健康检查接口的成功与失败响应
- 阶段 2 基础数据表和关键列
- 注册 / 登录
- TXT / Markdown / OCR JSON 上传、解析与 chunk 入库
- 本地目录导入
- OCR JSON 表格 chunk 与 OCR 结构化记录入库
- Embedding provider 维度配置
- VectorIndexService 向量化状态回写、Redis 命中后回查 MySQL
- `/api/v1/rag/index`、`/api/v1/rag/search`、`/api/v1/rag/index/status` 接口契约
- `/api/v1/rag/ask` 问答接口契约
- RAG Chain 提示词构建、LLM 调用、无依据拒答和 `rag_query_logs` 日志写入
- AI 任务优化、任务拆分、AI 补充任务、月历统计和批量创建接口契约
- 日期任务查询、状态更新、任务反馈和轻量调整接口契约
- RAG 检索和回答来源返回
- 不支持格式不写入占位 chunk
- 用户之间文档、chunk、检索结果隔离

## 后续建议

1. 为导入流程增加解析错误详情字段和导入任务表，便于批量导入的失败重试与质量评估。
2. 为向量化增加后台任务、导入后自动索引、失败重试和索引一致性巡检。
3. 增加 RAG 评估集、命中率、引用覆盖率和无依据拒答率统计。
4. 为任务日历增加完成率、延期率、实际用时偏差和长期任务推进统计。
5. 为任务日历增加周视图和拖拽调整顺序。
