import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from devlog.api.main import app
from devlog.api.deps import get_db
from devlog.db import Base


@pytest.fixture(scope="function")
def client():
    # StaticPool makes all SQLAlchemy sessions share one connection,
    # so the in-memory database persists across requests in the same test.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_start_session(client):
    r = client.post("/sessions", json={"description": "building the API"})
    assert r.status_code == 201
    data = r.json()
    assert data["description"] == "building the API"
    assert data["is_active"] is True
    assert data["end_time"] is None


def test_cannot_start_duplicate_session(client):
    client.post("/sessions", json={"description": "first"})
    r = client.post("/sessions", json={"description": "second"})
    assert r.status_code == 409


def test_stop_session(client):
    created = client.post("/sessions", json={"description": "test"}).json()
    r = client.patch(f"/sessions/{created['id']}/stop")
    assert r.status_code == 200
    data = r.json()
    assert data["is_active"] is False
    assert data["end_time"] is not None


def test_stop_nonexistent_session(client):
    r = client.patch("/sessions/999/stop")
    assert r.status_code == 404


def test_tag_session(client):
    created = client.post("/sessions", json={"description": "test"}).json()
    r = client.post(f"/sessions/{created['id']}/tags", json={"names": ["python", "fastapi"]})
    assert r.status_code == 200
    tag_names = [t["name"] for t in r.json()["tags"]]
    assert "python" in tag_names
    assert "fastapi" in tag_names


def test_list_sessions_empty(client):
    r = client.get("/sessions")
    assert r.status_code == 200
    assert r.json() == []


def test_list_sessions_returns_created(client):
    client.post("/sessions", json={"description": "session one"})
    r = client.get("/sessions?all=true")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_get_single_session(client):
    created = client.post("/sessions", json={"description": "get me"}).json()
    r = client.get(f"/sessions/{created['id']}")
    assert r.status_code == 200
    assert r.json()["description"] == "get me"


def test_list_tags(client):
    created = client.post("/sessions", json={"description": "test"}).json()
    client.post(f"/sessions/{created['id']}/tags", json={"names": ["sql", "alembic"]})
    r = client.get("/tags")
    assert r.status_code == 200
    names = [t["name"] for t in r.json()]
    assert "sql" in names
    assert "alembic" in names
