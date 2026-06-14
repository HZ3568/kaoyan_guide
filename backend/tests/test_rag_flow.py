import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app


@pytest.fixture()
def client(tmp_path):
    old_raw_data_dir = settings.RAW_DATA_DIR
    old_auto_create_tables = settings.AUTO_CREATE_TABLES
    settings.RAW_DATA_DIR = str(tmp_path / "raw")
    settings.AUTO_CREATE_TABLES = False

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        settings.RAW_DATA_DIR = old_raw_data_dir
        settings.AUTO_CREATE_TABLES = old_auto_create_tables


def auth_headers(client: TestClient, username: str) -> dict[str, str]:
    payload = {"username": username, "password": "password123"}
    register_res = client.post("/api/v1/auth/register", json=payload)
    assert register_res.status_code == 200

    login_res = client.post("/api/v1/auth/login", json=payload)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_txt_upload_rag_citations_and_user_isolation(client: TestClient):
    user_a = auth_headers(client, "alice")
    user_b = auth_headers(client, "bob")

    upload_res = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "math.txt",
                "高等数学 极限 导数 积分 是数学复习重点。".encode("utf-8"),
                "text/plain",
            )
        },
        headers=user_a,
    )
    assert upload_res.status_code == 200
    doc = upload_res.json()
    assert doc["parse_status"] == "parsed"

    chunks_res = client.get(f"/api/v1/documents/{doc['id']}/chunks", headers=user_a)
    assert chunks_res.status_code == 200
    chunks = chunks_res.json()
    assert len(chunks) == 1
    assert "极限" in chunks[0]["content"]

    retrieve_res = client.post(
        "/api/v1/rag/retrieve",
        json={"query": "极限", "top_k": 5},
        headers=user_a,
    )
    assert retrieve_res.status_code == 200
    retrieved = retrieve_res.json()
    assert len(retrieved) == 1
    assert retrieved[0]["document_id"] == doc["id"]

    chat_res = client.post(
        "/api/v1/rag/chat",
        json={"question": "极限怎么复习？"},
        headers=user_a,
    )
    assert chat_res.status_code == 200
    chat = chat_res.json()
    assert chat["citations"][0]["document_id"] == doc["id"]
    assert chat["retrieval_debug"]["mode"] == "keyword_placeholder"

    unrelated_chat = client.post(
        "/api/v1/rag/chat",
        json={"question": "英语作文怎么复习？"},
        headers=user_a,
    )
    assert unrelated_chat.status_code == 200
    assert unrelated_chat.json()["citations"] == []

    assert client.get("/api/v1/documents", headers=user_b).json() == []
    assert client.get(f"/api/v1/documents/{doc['id']}/chunks", headers=user_b).status_code == 404

    isolated_retrieve = client.post(
        "/api/v1/rag/retrieve",
        json={"query": "极限", "top_k": 5},
        headers=user_b,
    )
    assert isolated_retrieve.status_code == 200
    assert isolated_retrieve.json() == []

    isolated_chat = client.post(
        "/api/v1/rag/chat",
        json={"question": "极限怎么复习？"},
        headers=user_b,
    )
    assert isolated_chat.status_code == 200
    assert isolated_chat.json()["citations"] == []


def test_unsupported_upload_does_not_create_placeholder_chunks(client: TestClient):
    user = auth_headers(client, "charlie")

    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("guide.pdf", b"%PDF-1.4 mock", "application/pdf")},
        headers=user,
    )
    assert upload_res.status_code == 200
    doc = upload_res.json()
    assert doc["parse_status"] == "unsupported"

    chunks_res = client.get(f"/api/v1/documents/{doc['id']}/chunks", headers=user)
    assert chunks_res.status_code == 200
    assert chunks_res.json() == []
