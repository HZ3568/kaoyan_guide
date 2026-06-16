from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.goal import Goal
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from app.planner.task_models import DailyReview, TaskExecutionSession, TaskItem
from app.planner.task_schemas import TaskItemCreate
from app.planner.task_service import TaskService
from app.rag.vector_store import RedisVectorHit
from app.schemas.rag import RetrievalFilter
from app.schemas.rag import RagAskResponse
from app.services.rag_service import NO_EVIDENCE_ANSWER, RagService
from app.services.vector_index_service import VectorIndexService


def make_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()


def test_general_schema_tables_and_columns():
    db = make_session()
    try:
        inspector = inspect(db.bind)
        tables = set(inspector.get_table_names())
        assert {
            "users",
            "user_profiles",
            "goals",
            "knowledge_bases",
            "documents",
            "document_chunks",
            "rag_query_logs",
            "task_items",
            "task_execution_sessions",
            "daily_reviews",
        } <= tables

        document_columns = {column["name"] for column in inspector.get_columns("documents")}
        assert {"knowledge_base_id", "goal_id", "domain", "category", "chunk_count"} <= document_columns
        assert not {"school", "major", "exam_year", "subject"} & document_columns

        task_columns = {column["name"] for column in inspector.get_columns("task_items")}
        assert {"content", "planned_date", "actual_minutes", "source_type"} <= task_columns
        assert "subject" not in task_columns
    finally:
        db.close()


def test_auth_onboarding_goal_kb_document_task_review_flow(tmp_path):
    old_raw_dir = settings.RAW_DATA_DIR
    settings.RAW_DATA_DIR = str(tmp_path)
    db = make_session()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)
        auth_payload = {"username": "general-user", "password": "password123"}
        assert client.post("/api/v1/auth/register", json=auth_payload).status_code == 200
        login_res = client.post("/api/v1/auth/login", json=auth_payload)
        headers = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

        onboarding_res = client.post(
            "/api/v1/profiles/onboarding",
            json={
                "profile": {
                    "persona_type": "student",
                    "current_stage": "foundation",
                    "domain": "software",
                    "daily_available_minutes": 120,
                    "weekly_available_days": 5,
                },
                "goal": {
                    "title": "Build a RAG project",
                    "goal_type": "project",
                    "domain": "software",
                    "target_result": "Ship a working demo",
                    "deadline": str(date.today()),
                    "priority": "high",
                },
            },
            headers=headers,
        )
        assert onboarding_res.status_code == 200
        goal_id = onboarding_res.json()["goal"]["id"]

        kb_res = client.post(
            "/api/v1/knowledge-bases",
            json={"name": "Project Notes", "goal_id": goal_id, "domain": "software"},
            headers=headers,
        )
        assert kb_res.status_code == 200
        kb_id = kb_res.json()["id"]

        upload_res = client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("notes.md", b"# RAG\n\nUse chunking before indexing.", "text/markdown")},
            data={"knowledge_base_id": str(kb_id), "goal_id": str(goal_id), "domain": "software", "category": "backend"},
        )
        assert upload_res.status_code == 200
        document_id = upload_res.json()["id"]
        chunks_res = client.get(f"/api/v1/documents/{document_id}/chunks", headers=headers)
        assert chunks_res.status_code == 200
        chunk = chunks_res.json()[0]
        assert chunk["goal_id"] == goal_id
        assert chunk["knowledge_base_id"] == kb_id
        assert chunk["domain"] == "software"
        assert chunk["category"] == "backend"

        task_res = client.post(
            "/api/v1/tasks",
            json={
                "content": "Summarize chunking design",
                "goal_id": goal_id,
                "category": "backend",
                "planned_date": str(date.today()),
                "estimated_minutes": 45,
            },
            headers=headers,
        )
        assert task_res.status_code == 200
        task_id = task_res.json()["id"]
        list_res = client.get(f"/api/v1/tasks?goal_id={goal_id}&date={date.today()}", headers=headers)
        assert list_res.status_code == 200
        assert list_res.json()[0]["id"] == task_id

        start_res = client.post(f"/api/v1/tasks/{task_id}/start", headers=headers)
        assert start_res.status_code == 200
        second_task = client.post(
            "/api/v1/tasks",
            json={"content": "Second task", "planned_date": str(date.today()), "estimated_minutes": 30},
            headers=headers,
        ).json()
        blocked = client.post(f"/api/v1/tasks/{second_task['id']}/start", headers=headers)
        assert blocked.status_code == 400

        complete_res = client.post(f"/api/v1/tasks/{task_id}/complete", json={"actual_minutes": 10}, headers=headers)
        assert complete_res.status_code == 200
        assert complete_res.json()["status"] == "completed"
        assert complete_res.json()["actual_minutes"] >= 0

        review_res = client.post(
            "/api/v1/reviews",
            json={
                "goal_id": goal_id,
                "review_date": str(date.today()),
                "completion_rate": 50,
                "summary": "Finished one task.",
            },
            headers=headers,
        )
        assert review_res.status_code == 200
        stats_res = client.get(f"/api/v1/reviews/stats?goal_id={goal_id}", headers=headers)
        assert stats_res.status_code == 200
        assert stats_res.json()["total_tasks"] == 1
    finally:
        app.dependency_overrides.clear()
        settings.RAW_DATA_DIR = old_raw_dir
        db.close()


def test_rag_no_results_does_not_call_llm():
    class EmptyVectorService:
        def search(self, **kwargs):
            return []

    class FailingLLM:
        provider = "test"
        model = "test"

        def generate(self, messages):
            raise AssertionError("LLM should not be called without retrieval results")

    db = make_session()
    try:
        response = RagService(db, llm_client=FailingLLM(), vector_service=EmptyVectorService()).ask(
            "What should I read?",
            user_id=1,
            knowledge_base_id=1,
        )
        assert isinstance(response, RagAskResponse)
        assert response.answer == NO_EVIDENCE_ANSWER
        assert response.hit_source is False
        assert response.retrieval_debug["llm_called"] is False
    finally:
        db.close()


def test_task_service_records_execution_session():
    db = make_session()
    try:
        user = User(username="timer-user", password_hash="hash")
        db.add(user)
        db.commit()
        db.refresh(user)
        service = TaskService(db)
        task = service.create_task(user.id, TaskItemCreate(content="Practice focused reading", planned_date=date.today()))
        session = service.start_task(user.id, task.id)
        assert session.status == "running"
        completed = service.complete_task(user.id, task.id)
        assert completed.status == "completed"
        assert completed.actual_minutes is not None
        assert db.query(TaskExecutionSession).filter(TaskExecutionSession.task_id == task.id).count() == 1
        assert db.query(TaskItem).count() == 1
    finally:
        db.close()


def test_cross_user_resource_isolation(tmp_path):
    old_raw_dir = settings.RAW_DATA_DIR
    settings.RAW_DATA_DIR = str(tmp_path)
    db = make_session()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    def auth_headers(client: TestClient, username: str) -> dict[str, str]:
        payload = {"username": username, "password": "password123"}
        assert client.post("/api/v1/auth/register", json=payload).status_code == 200
        login_res = client.post("/api/v1/auth/login", json=payload)
        assert login_res.status_code == 200
        return {"Authorization": f"Bearer {login_res.json()['access_token']}"}

    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)
        headers_a = auth_headers(client, "user-a")
        headers_b = auth_headers(client, "user-b")

        goal_b = client.post(
            "/api/v1/goals",
            json={"title": "Private goal", "goal_type": "project", "domain": "writing"},
            headers=headers_b,
        ).json()
        kb_b = client.post(
            "/api/v1/knowledge-bases",
            json={"name": "Private KB", "goal_id": goal_b["id"], "domain": "writing"},
            headers=headers_b,
        ).json()
        upload_b = client.post(
            "/api/v1/documents/upload",
            headers=headers_b,
            files={"file": ("private.md", b"# Private\n\nOnly user B can read this.", "text/markdown")},
            data={
                "knowledge_base_id": str(kb_b["id"]),
                "goal_id": str(goal_b["id"]),
                "domain": "writing",
                "category": "notes",
            },
        ).json()
        task_b = client.post(
            "/api/v1/tasks",
            json={
                "content": "Private task",
                "goal_id": goal_b["id"],
                "planned_date": str(date.today()),
                "estimated_minutes": 30,
            },
            headers=headers_b,
        ).json()
        review_b = client.post(
            "/api/v1/reviews",
            json={"goal_id": goal_b["id"], "review_date": str(date.today()), "summary": "Private review"},
            headers=headers_b,
        ).json()

        kb_a = client.post("/api/v1/knowledge-bases", json={"name": "User A KB"}, headers=headers_a).json()
        assert client.post(f"/api/v1/knowledge-bases/{kb_a['id']}/bind-goal/{goal_b['id']}", headers=headers_a).status_code == 404
        assert client.get(f"/api/v1/knowledge-bases/{kb_b['id']}", headers=headers_a).status_code == 404
        assert client.get(f"/api/v1/documents/{upload_b['id']}", headers=headers_a).status_code == 404
        assert client.get(f"/api/v1/tasks/{task_b['id']}", headers=headers_a).status_code == 404
        assert client.patch(f"/api/v1/reviews/{review_b['id']}", json={"summary": "steal"}, headers=headers_a).status_code == 404
        assert client.get(f"/api/v1/tasks?goal_id={goal_b['id']}", headers=headers_a).status_code == 404
        assert client.get(f"/api/v1/reviews/stats?goal_id={goal_b['id']}", headers=headers_a).status_code == 404
        assert client.post(
            "/api/v1/rag/ask",
            json={"question": "What is inside?", "knowledge_base_id": kb_b["id"]},
            headers=headers_a,
        ).status_code == 404
    finally:
        app.dependency_overrides.clear()
        settings.RAW_DATA_DIR = old_raw_dir
        db.close()


def test_vector_search_rechecks_user_id_against_mysql():
    class FakeEmbeddingProvider:
        dim = 3

        def embed_query(self, query: str):
            return [0.1, 0.2, 0.3]

    class FakeVectorStore:
        index_name = "idx:test"

        def __init__(self, hit: RedisVectorHit) -> None:
            self.hit = hit
            self.last_user_id = None

        def search(self, **kwargs):
            self.last_user_id = kwargs["user_id"]
            return [self.hit]

    db = make_session()
    try:
        user_a = User(username="rag-user-a", password_hash="hash")
        user_b = User(username="rag-user-b", password_hash="hash")
        db.add_all([user_a, user_b])
        db.commit()
        db.refresh(user_a)
        db.refresh(user_b)
        goal_b = Goal(user_id=user_b.id, title="B goal", goal_type="project")
        db.add(goal_b)
        db.commit()
        db.refresh(goal_b)
        kb_b = KnowledgeBase(user_id=user_b.id, goal_id=goal_b.id, name="B KB")
        db.add(kb_b)
        db.commit()
        db.refresh(kb_b)
        document_b = Document(
            user_id=user_b.id,
            goal_id=goal_b.id,
            knowledge_base_id=kb_b.id,
            filename="b.md",
            original_filename="b.md",
            file_type="md",
            file_path="/tmp/b.md",
            parse_status="completed",
            chunk_status="completed",
            embedding_status="indexed",
            chunk_count=1,
        )
        db.add(document_b)
        db.commit()
        db.refresh(document_b)
        chunk_b = DocumentChunk(
            document_id=document_b.id,
            user_id=user_b.id,
            goal_id=goal_b.id,
            knowledge_base_id=kb_b.id,
            chunk_index=0,
            content="User B private chunk",
            content_hash="hash-b",
            embedding_status="indexed",
        )
        db.add(chunk_b)
        db.commit()
        db.refresh(chunk_b)

        store = FakeVectorStore(RedisVectorHit(chunk_b.id, document_b.id, 0.1, 0.1, "learning:chunk:b"))
        service = VectorIndexService(db, embedding_provider=FakeEmbeddingProvider(), vector_store=store)
        assert service.search(query="private", user_id=user_a.id, filters=RetrievalFilter()) == []
        assert store.last_user_id == user_a.id
    finally:
        db.close()
