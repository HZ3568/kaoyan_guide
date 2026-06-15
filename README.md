# kaoyan-guide

基于 **Python + FastAPI + React + MySQL + Redis Vector** 的考研 RAG 知识库与智能学习规划系统骨架。

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
- RAG retrieve/chat 占位接口，当前按用户隔离检索并返回来源 chunk
- 学习画像、学习计划、每日任务占位接口

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

Docker Compose 默认读取 `backend/.env.example` 中的开发占位配置，并在容器内把后端 MySQL 地址覆盖为 `mysql:3306`。

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
- `learning_profiles` / `learning_plans` / `learning_tasks`：学习画像、规划内容和任务记录。
- `chat_sessions` / `chat_messages`：问答会话和消息记录。

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
- RAG 检索和回答来源返回
- 不支持格式不写入占位 chunk
- 用户之间文档、chunk、检索结果隔离

## 后续建议

1. 为导入流程增加解析错误详情字段和导入任务表，便于批量导入的失败重试与质量评估。
2. 将 `RagService` 的回答生成切到 Redis Vector 检索结果，并保留关键词兜底与来源约束。
3. 新增统一 LLM Provider 接口，将 `RagService` 接入真实大模型并保留引用约束。
4. 为向量化增加后台任务、导入后自动索引、失败重试和索引一致性巡检。
5. 将 `PlannerService` 改造为结构化 JSON 计划生成、规则校验与任务反馈闭环。
