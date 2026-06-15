from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.user import User
from app.rag.vector_store import RedisVectorHit
from app.services.embedding_service import MockEmbeddingProvider, get_embedding_provider
from app.services.vector_index_service import (
    VectorIndexResult,
    VectorIndexService,
    VectorSearchResult,
)


class FakeVectorStore:
    index_name = "idx:test"
    key_prefix = "test:chunk"

    def __init__(self) -> None:
        self.upserts = []

    def ensure_index(self) -> None:
        return None

    def upsert_chunk(self, **kwargs):
        self.upserts.append(kwargs)
        return f"{self.key_prefix}:{kwargs['chunk_id']}"

    def search(self, **kwargs):
        chunk_id = self.upserts[0]["chunk_id"] if self.upserts else 1
        document_id = self.upserts[0]["document_id"] if self.upserts else 1
        return [
            RedisVectorHit(
                chunk_id=chunk_id,
                document_id=document_id,
                score=0.88,
                distance=0.12,
                redis_key=f"{self.key_prefix}:{chunk_id}",
            )
        ]

    def index_info(self):
        return {
            "exists": True,
            "index_name": self.index_name,
            "key_prefix": self.key_prefix,
            "embedding_dim": 4,
            "num_docs": len(self.upserts),
        }


def make_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)()


def seed_chunk(db):
    user = User(username="vector-user", password_hash="hash")
    db.add(user)
    db.flush()
    document = Document(
        user_id=user.id,
        title="数学资料",
        file_name="math.txt",
        file_type=".txt",
        file_path="/tmp/math.txt",
        source="本地资料",
        source_type="uploaded",
        subject="数学",
        parse_status="parsed",
    )
    db.add(document)
    db.flush()
    chunk = DocumentChunk(
        document_id=document.id,
        chunk_index=0,
        content="极限、导数和积分是数学复习重点。",
        chunk_type="text",
        content_hash="hash",
        token_count=16,
        metadata_json={"title": document.title},
        embedding_status="pending",
        is_vectorized=False,
    )
    db.add(chunk)
    db.commit()
    return user, document, chunk


def test_mock_embedding_uses_configured_dimension():
    provider = MockEmbeddingProvider(dim=12)
    assert len(provider.embed_query("极限")) == 12
    assert len(provider.embed_documents(["极限", "导数"])) == 2


def test_embedding_factory_respects_configured_dimension():
    old_dim = settings.EMBEDDING_DIM
    old_provider = settings.EMBEDDING_PROVIDER
    settings.EMBEDDING_DIM = 8
    settings.EMBEDDING_PROVIDER = "mock"
    try:
        provider = get_embedding_provider()
        assert provider.dim == 8
        assert len(provider.embed_query("数学")) == 8
    finally:
        settings.EMBEDDING_DIM = old_dim
        settings.EMBEDDING_PROVIDER = old_provider


def test_vector_index_service_indexes_and_searches_mysql_chunks():
    db = make_session()
    try:
        user, document, chunk = seed_chunk(db)
        store = FakeVectorStore()
        service = VectorIndexService(
            db,
            embedding_provider=MockEmbeddingProvider(dim=4),
            vector_store=store,
        )

        index_result = service.index_pending(user_id=user.id, batch_size=1)
        db.refresh(chunk)

        assert index_result.indexed == 1
        assert chunk.is_vectorized is True
        assert chunk.embedding_status == "indexed"
        assert chunk.vector_index_key == f"{store.key_prefix}:{chunk.id}"
        assert store.upserts[0]["document_id"] == document.id

        search_result = service.search(query="极限", user_id=user.id, top_k=1)
        assert len(search_result) == 1
        assert search_result[0].chunk_id == chunk.id
        assert search_result[0].document_id == document.id
        assert search_result[0].source["title"] == "数学资料"
        assert "极限" in search_result[0].content
    finally:
        db.close()


def test_rag_vector_api_contract(monkeypatch):
    old_auto_create_tables = settings.AUTO_CREATE_TABLES
    settings.AUTO_CREATE_TABLES = False
    db = make_session()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    class FakeVectorIndexService:
        def __init__(self, db):
            self.db = db

        def index_pending(self, **kwargs):
            return VectorIndexResult(
                indexed=2,
                skipped=0,
                failed=0,
                errors=[],
                index_name="idx:test",
                embedding_dim=4,
            )

        def status(self, **kwargs):
            return {
                "total_chunks": 2,
                "indexed_chunks": 2,
                "pending_chunks": 0,
                "failed_chunks": 0,
                "redis": {"exists": True, "index_name": "idx:test"},
            }

        def search(self, **kwargs):
            return [
                VectorSearchResult(
                    chunk_id=1,
                    document_id=1,
                    score=0.9,
                    content="极限、导数和积分是数学复习重点。",
                    source={"title": "数学资料", "source": "本地资料"},
                    page_number=None,
                    location={"position_start": None, "position_end": None},
                    metadata={"subject": "数学"},
                )
            ]

    monkeypatch.setattr("app.api.v1.rag.VectorIndexService", FakeVectorIndexService)
    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)
        register_res = client.post(
            "/api/v1/auth/register",
            json={"username": "vector-api", "password": "password123"},
        )
        assert register_res.status_code == 200
        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": "vector-api", "password": "password123"},
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        index_res = client.post("/api/v1/rag/index", json={"limit": 10}, headers=headers)
        assert index_res.status_code == 200
        assert index_res.json()["indexed"] == 2

        status_res = client.get("/api/v1/rag/index/status", headers=headers)
        assert status_res.status_code == 200
        assert status_res.json()["redis"]["index_name"] == "idx:test"

        search_res = client.post(
            "/api/v1/rag/search",
            json={"query": "极限怎么复习", "top_k": 3},
            headers=headers,
        )
        assert search_res.status_code == 200
        payload = search_res.json()
        assert payload[0]["chunk_id"] == 1
        assert payload[0]["source"]["title"] == "数学资料"
        assert payload[0]["metadata"]["subject"] == "数学"
    finally:
        app.dependency_overrides.clear()
        db.close()
        settings.AUTO_CREATE_TABLES = old_auto_create_tables
