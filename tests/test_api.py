import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from devlog.api.main import app
from devlog.api.deps import get_db
from devlog.api.auth import hash_password, create_token
from devlog.db import Base
from devlog.models import User


@pytest.fixture(scope="function")
def client():
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
        c._test_db = TestSession
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


@pytest.fixture
def auth_client(client):
    """Create a test user directly in the DB (bypasses rate limiting) and set auth header."""
    db = client._test_db()
    user = User(email="test@example.com", hashed_password=hash_password("testpass123"))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token(user.id)
    db.close()
    client.headers["Authorization"] = f"Bearer {token}"
    return client


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_register(client):
    r = client.post("/auth/register", json={"email": "new@example.com", "password": "pass123"})
    assert r.status_code == 201
    assert "access_token" in r.json()


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "pass"}
    client.post("/auth/register", json=payload)
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 409


def test_login(client):
    client.post("/auth/register", json={"email": "login@example.com", "password": "pass"})
    r = client.post("/auth/login", json={"email": "login@example.com", "password": "pass"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "wp@example.com", "password": "correct"})
    r = client.post("/auth/login", json={"email": "wp@example.com", "password": "wrong"})
    assert r.status_code == 401


def test_sessions_require_auth(client):
    r = client.get("/sessions")
    assert r.status_code == 401


def test_start_session(auth_client):
    r = auth_client.post("/sessions", json={"description": "building the API"})
    assert r.status_code == 201
    data = r.json()
    assert data["description"] == "building the API"
    assert data["is_active"] is True
    assert data["end_time"] is None


def test_cannot_start_duplicate_session(auth_client):
    auth_client.post("/sessions", json={"description": "first"})
    r = auth_client.post("/sessions", json={"description": "second"})
    assert r.status_code == 409


def test_stop_session(auth_client):
    created = auth_client.post("/sessions", json={"description": "test"}).json()
    r = auth_client.patch(f"/sessions/{created['id']}/stop")
    assert r.status_code == 200
    assert r.json()["is_active"] is False


def test_stop_nonexistent_session(auth_client):
    r = auth_client.patch("/sessions/999/stop")
    assert r.status_code == 404


def test_tag_session(auth_client):
    created = auth_client.post("/sessions", json={"description": "test"}).json()
    r = auth_client.post(f"/sessions/{created['id']}/tags", json={"names": ["python", "fastapi"]})
    assert r.status_code == 200
    tag_names = [t["name"] for t in r.json()["tags"]]
    assert "python" in tag_names
    assert "fastapi" in tag_names


def test_list_sessions_empty(auth_client):
    r = auth_client.get("/sessions")
    assert r.status_code == 200
    assert r.json() == []


def test_list_sessions_returns_created(auth_client):
    auth_client.post("/sessions", json={"description": "session one"})
    r = auth_client.get("/sessions?all=true")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_get_single_session(auth_client):
    created = auth_client.post("/sessions", json={"description": "get me"}).json()
    r = auth_client.get(f"/sessions/{created['id']}")
    assert r.status_code == 200
    assert r.json()["description"] == "get me"


def test_list_tags(auth_client):
    created = auth_client.post("/sessions", json={"description": "test"}).json()
    auth_client.post(f"/sessions/{created['id']}/tags", json={"names": ["sql", "alembic"]})
    r = auth_client.get("/tags")
    assert r.status_code == 200
    names = [t["name"] for t in r.json()]
    assert "sql" in names
    assert "alembic" in names


def test_users_cannot_see_each_others_sessions(client):
    db = client._test_db()
    alice = User(email="alice@x.com", hashed_password=hash_password("pass"))
    bob = User(email="bob@x.com", hashed_password=hash_password("pass"))
    db.add_all([alice, bob])
    db.commit()
    db.refresh(alice)
    db.refresh(bob)
    token_a = create_token(alice.id)
    token_b = create_token(bob.id)
    db.close()

    client.headers["Authorization"] = f"Bearer {token_a}"
    created = client.post("/sessions", json={"description": "alice's session"}).json()

    client.headers["Authorization"] = f"Bearer {token_b}"
    r = client.get(f"/sessions/{created['id']}")
    assert r.status_code == 404
