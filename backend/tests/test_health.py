from fastapi.testclient import TestClient

from app.main import app
from app.services import health_service


def test_health():
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_dependency_health_checks_ok(monkeypatch):
    monkeypatch.setattr(
        health_service,
        "check_database",
        lambda: {"status": "ok", "component": "mysql"},
    )
    monkeypatch.setattr(
        health_service,
        "check_redis",
        lambda: {"status": "ok", "component": "redis"},
    )

    client = TestClient(app)

    db_res = client.get("/health/db")
    assert db_res.status_code == 200
    assert db_res.json() == {"status": "ok", "component": "mysql"}

    redis_res = client.get("/health/redis")
    assert redis_res.status_code == 200
    assert redis_res.json() == {"status": "ok", "component": "redis"}


def test_dependency_health_checks_return_503(monkeypatch):
    monkeypatch.setattr(
        health_service,
        "check_database",
        lambda: {"status": "error", "component": "mysql", "error": "OperationalError"},
    )
    monkeypatch.setattr(
        health_service,
        "check_redis",
        lambda: {"status": "error", "component": "redis", "error": "ConnectionError"},
    )

    client = TestClient(app)

    db_res = client.get("/health/db")
    assert db_res.status_code == 503
    assert db_res.json()["component"] == "mysql"

    redis_res = client.get("/health/redis")
    assert redis_res.status_code == 503
    assert redis_res.json()["component"] == "redis"
