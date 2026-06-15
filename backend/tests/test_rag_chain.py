from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.core.config import settings
from app.core.database import Base, get_db
from app.llm.client import LLMResponse
from app.main import app
from app.models.rag_log import RagQueryLog
from app.models.user import User
from app.schemas.rag import RagAskResponse, RagSource
from app.services.rag_service import RagService
from app.services.vector_index_service import VectorSearchResult


def make_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()


class FakeLLMClient:
    provider = "fake"
    model = "fake-model"

    def __init__(self) -> None:
        self.messages = []

    def generate(self, messages, **kwargs):
        self.messages = messages
        return LLMResponse(
            content="北京大学计算机科学与技术复试线为 350，招生人数为 20。[来源1]",
            provider=self.provider,
            model=self.model,
        )


class FakeVectorService:
    def __init__(self, chunks):
        self.chunks = chunks
        self.calls = []

    def search(self, **kwargs):
        self.calls.append(kwargs)
        return self.chunks


def seed_user(db):
    user = User(username="rag-chain-user", password_hash="hash")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_result():
    return VectorSearchResult(
        chunk_id=11,
        document_id=7,
        score=0.91,
        content="院校：北京大学\n专业：计算机科学与技术\n分数线：350\n招生人数：20",
        source={
            "document_id": 7,
            "title": "北京大学计算机招生目录",
            "source": "OCR招生目录",
            "source_type": "uploaded",
            "source_url": None,
            "file_name": "ocr.json",
            "file_type": ".json",
            "page_number": 1,
        },
        page_number=1,
        location={"position_start": None, "position_end": None},
        metadata={"table_fields": {"school": "北京大学", "major": "计算机科学与技术"}},
    )


def test_rag_ask_uses_context_and_writes_source_log():
    db = make_session()
    try:
        user = seed_user(db)
        fake_llm = FakeLLMClient()
        service = RagService(
            db,
            llm_client=fake_llm,
            vector_service=FakeVectorService([make_result()]),
        )

        response = service.ask("北京大学计算机分数线是多少？", user_id=user.id, top_k=3)

        assert response.hit_source is True
        assert response.sources[0].chunk_id == 11
        assert response.sources[0].title == "北京大学计算机招生目录"
        assert "350" in response.answer
        assert "只根据给定的检索上下文回答问题" in fake_llm.messages[0].content
        assert "分数线：350" in fake_llm.messages[1].content

        log = db.query(RagQueryLog).filter(RagQueryLog.id == response.log_id).one()
        assert log.user_id == user.id
        assert log.hit_source is True
        assert log.retrieved_chunks_json[0]["chunk_id"] == 11
        assert log.model_provider == "fake"
        assert "350" in log.model_answer
    finally:
        db.close()


def test_rag_ask_without_chunks_refuses_and_logs_no_source():
    db = make_session()
    try:
        user = seed_user(db)
        fake_llm = FakeLLMClient()
        service = RagService(
            db,
            llm_client=fake_llm,
            vector_service=FakeVectorService([]),
        )

        response = service.ask("清华大学某专业分数线是多少？", user_id=user.id)

        assert response.hit_source is False
        assert response.sources == []
        assert "当前知识库没有找到依据" in response.answer
        assert fake_llm.messages == []

        log = db.query(RagQueryLog).filter(RagQueryLog.id == response.log_id).one()
        assert log.hit_source is False
        assert log.retrieved_chunks_json == []
        assert "当前知识库没有找到依据" in log.model_answer
    finally:
        db.close()


def test_rag_ask_api_contract(monkeypatch):
    old_auto_create_tables = settings.AUTO_CREATE_TABLES
    settings.AUTO_CREATE_TABLES = False
    db = make_session()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    class FakeRagService:
        def __init__(self, db):
            self.db = db

        def ask(self, question, **kwargs):
            return RagAskResponse(
                answer="根据资料，极限和导数是高等数学重点。[来源1]",
                sources=[
                    RagSource(
                        chunk_id=1,
                        document_id=2,
                        score=0.87,
                        title="数学资料",
                        source="本地资料",
                        source_type="uploaded",
                        file_name="math.txt",
                        page_number=None,
                        location={},
                        content_preview="高等数学 极限 导数 积分 是数学复习重点。",
                        metadata={"subject": "数学"},
                    )
                ],
                hit_source=True,
                model_provider="fake",
                model_name="fake-model",
                log_id=9,
                retrieval_debug={"mode": "vector_rag", "retrieved": 1},
            )

    monkeypatch.setattr("app.api.v1.rag.RagService", FakeRagService)
    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)
        auth_payload = {"username": "rag-api", "password": "password123"}
        assert client.post("/api/v1/auth/register", json=auth_payload).status_code == 200
        login_res = client.post("/api/v1/auth/login", json=auth_payload)
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        ask_res = client.post(
            "/api/v1/rag/ask",
            json={"question": "极限怎么复习？", "top_k": 3, "stream": False},
            headers=headers,
        )
        assert ask_res.status_code == 200
        payload = ask_res.json()
        assert payload["hit_source"] is True
        assert payload["sources"][0]["chunk_id"] == 1
        assert payload["log_id"] == 9
        assert payload["retrieval_debug"]["mode"] == "vector_rag"
    finally:
        app.dependency_overrides.clear()
        db.close()
        settings.AUTO_CREATE_TABLES = old_auto_create_tables
