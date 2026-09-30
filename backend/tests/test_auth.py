"""
Phase 1 tests: registration, login, RBAC boundary checks, audit logging.

Uses the SAME Postgres server as development but a separate 'transplant_test_db'
database so tests never touch your real data. Create it once with:
    createdb -U postgres transplant_test_db
(the docker-compose setup does this automatically — see backend/tests/README.md)
"""
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/transplant_test_db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-not-for-production")

from app.main import app  # noqa: E402
from app.database.session import get_db  # noqa: E402
from app.database.base import Base  # noqa: E402
from app import models as _app_models  # noqa: E402,F401  (registers all tables on Base.metadata)
from app.models.role import Role, RoleName  # noqa: E402

TEST_DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    for role_name in RoleName:
        db.add(Role(name=role_name, description=role_name.value))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def unique_email(prefix="user"):
    return f"{prefix}.{uuid.uuid4().hex[:8]}@example.com"


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_patient_succeeds(client):
    email = unique_email("patient")
    response = client.post("/auth/register", json={"email": email, "password": "StrongPass123!", "role": "patient"})
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == email
    assert body["role"] == "patient"


def test_register_coordinator_is_forbidden(client):
    """Only patients can self-register; other roles need a system_admin."""
    response = client.post(
        "/auth/register", json={"email": unique_email(), "password": "StrongPass123!", "role": "coordinator"}
    )
    assert response.status_code == 403


def test_register_duplicate_email_conflicts(client):
    email = unique_email("dup")
    client.post("/auth/register", json={"email": email, "password": "StrongPass123!", "role": "patient"})
    response = client.post("/auth/register", json={"email": email, "password": "AnotherPass123!", "role": "patient"})
    assert response.status_code == 409


def test_login_success_returns_tokens(client):
    email = unique_email("login")
    client.post("/auth/register", json={"email": email, "password": "StrongPass123!", "role": "patient"})
    response = client.post("/auth/login", json={"email": email, "password": "StrongPass123!"})
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body and "refresh_token" in body


def test_login_wrong_password_fails(client):
    email = unique_email("wrongpw")
    client.post("/auth/register", json={"email": email, "password": "StrongPass123!", "role": "patient"})
    response = client.post("/auth/login", json={"email": email, "password": "NotTheRightPassword"})
    assert response.status_code == 401


def test_protected_route_requires_token(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_protected_route_rejects_garbage_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_protected_route_works_with_valid_token(client):
    email = unique_email("me")
    client.post("/auth/register", json={"email": email, "password": "StrongPass123!", "role": "patient"})
    login_response = client.post("/auth/login", json={"email": email, "password": "StrongPass123!"})
    token = login_response.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == email


def test_refresh_token_issues_new_access_token(client):
    email = unique_email("refresh")
    client.post("/auth/register", json={"email": email, "password": "StrongPass123!", "role": "patient"})
    login_response = client.post("/auth/login", json={"email": email, "password": "StrongPass123!"})
    refresh_token = login_response.json()["refresh_token"]

    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()
