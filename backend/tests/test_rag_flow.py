import json

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
    old_data_dir = settings.DATA_DIR
    old_raw_data_dir = settings.RAW_DATA_DIR
    old_local_import_root = settings.LOCAL_IMPORT_ROOT
    old_auto_create_tables = settings.AUTO_CREATE_TABLES
    settings.DATA_DIR = str(tmp_path)
    settings.RAW_DATA_DIR = str(tmp_path / "raw")
    settings.LOCAL_IMPORT_ROOT = str(tmp_path)
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
        settings.DATA_DIR = old_data_dir
        settings.RAW_DATA_DIR = old_raw_data_dir
        settings.LOCAL_IMPORT_ROOT = old_local_import_root
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
        files={"file": ("guide.docx", b"mock docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        headers=user,
    )
    assert upload_res.status_code == 200
    doc = upload_res.json()
    assert doc["parse_status"] == "unsupported"

    chunks_res = client.get(f"/api/v1/documents/{doc['id']}/chunks", headers=user)
    assert chunks_res.status_code == 200
    assert chunks_res.json() == []


def test_ocr_json_upload_generates_table_chunk_with_source_metadata(client: TestClient):
    user = auth_headers(client, "dora")
    payload = {
        "text": "北京大学计算机学院招生目录",
        "tables": [
            {
                "title": "招生目录",
                "rows": [
                    {
                        "院校": "北京大学",
                        "专业": "计算机科学与技术",
                        "研究方向": "人工智能",
                        "考试科目": "101思想政治理论; 201英语一; 408计算机学科专业基础",
                        "分数线": "350",
                        "招生人数": "20",
                    }
                ],
            }
        ],
    }

    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("ocr.json", json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json")},
        data={"source": "OCR招生目录", "tags": "计算机,招生目录"},
        headers=user,
    )
    assert upload_res.status_code == 200
    doc = upload_res.json()
    assert doc["parse_status"] == "parsed"
    assert doc["tags_json"] == ["计算机", "招生目录"]

    chunks_res = client.get(f"/api/v1/documents/{doc['id']}/chunks", headers=user)
    assert chunks_res.status_code == 200
    chunks = chunks_res.json()
    table_chunks = [chunk for chunk in chunks if chunk["chunk_type"] == "table"]
    assert len(table_chunks) == 1
    assert "院校：北京大学" in table_chunks[0]["content"]
    assert table_chunks[0]["metadata_json"]["table_fields"]["major"] == "计算机科学与技术"
    assert table_chunks[0]["metadata_json"]["source"] == "OCR招生目录"


def test_import_local_directory_generates_chunks(client: TestClient, tmp_path):
    user = auth_headers(client, "erin")
    import_dir = tmp_path / "imports"
    import_dir.mkdir()
    (import_dir / "math.md").write_text(
        "# 高等数学\n\n极限、导数和积分是数学复习重点。\n\n第二阶段需要配合真题训练。",
        encoding="utf-8",
    )

    import_res = client.post(
        "/api/v1/documents/import-local",
        json={
            "path": "imports",
            "source": "本地资料库",
            "subject": "数学",
            "tags": ["高数", "真题"],
        },
        headers=user,
    )
    assert import_res.status_code == 200
    payload = import_res.json()
    assert payload["errors"] == []
    assert len(payload["imported"]) == 1
    doc = payload["imported"][0]
    assert doc["parse_status"] == "parsed"
    assert doc["source_type"] == "local"

    chunks_res = client.get(f"/api/v1/documents/{doc['id']}/chunks", headers=user)
    assert chunks_res.status_code == 200
    chunks = chunks_res.json()
    assert len(chunks) == 1
    assert "极限" in chunks[0]["content"]
    assert chunks[0]["metadata_json"]["source_type"] == "local"
