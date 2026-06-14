# kaoyan-guide

基于 **Python + FastAPI + React + MySQL + Redis Vector** 的考研 RAG 知识库与智能学习规划系统骨架。

## 当前包含

- FastAPI 后端项目结构
- React + Vite + TypeScript 前端项目结构
- MySQL / Redis Stack docker-compose
- JWT 鉴权基础代码
- TXT / Markdown / CSV / JSON 文档上传、解析、chunk 入库流程
- PDF / Word / 图片等暂未解析格式会标记为 `unsupported`，不会写入占位 chunk
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

## 测试

```bash
cd backend
.venv\Scripts\python -m pytest  # Windows
```

当前测试覆盖：

- 健康检查
- 注册 / 登录
- TXT 上传、解析与 chunk 入库
- RAG 检索和回答来源返回
- 不支持格式不写入占位 chunk
- 用户之间文档、chunk、检索结果隔离

## 后续建议

1. 接入 Alembic 初始化数据库迁移，替代开发期 `create_all`。
2. 将 `IngestionService` 扩展为 PDF、Word、OCR、表格解析，并记录解析错误详情。
3. 将 `RetrievalService` 替换为 Redis Vector + BM25 + Rerank，MySQL 继续保存可信元数据。
4. 新增统一 LLM Provider 接口，将 `RagService` 接入真实大模型并保留引用约束。
5. 将 `PlannerService` 改造为结构化 JSON 计划生成、规则校验与任务反馈闭环。
