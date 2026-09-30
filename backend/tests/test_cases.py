"""
Phase 2 tests: case creation, ownership isolation, status state machine,
timeline, and input validation. Reuses the same test-DB fixture pattern
as tests/test_auth.py.
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
from app import models as _app_models  # noqa: E402,F401
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


def register_and_login(client, prefix="patient", role="patient"):
    email = unique_email(prefix)
    password = "StrongPass123!"
    if role != "patient":
        # Non-patient roles can't self-register (Phase 1 rule) — create directly via DB for test purposes.
        db = TestingSessionLocal()
        from app.repositories import user_repository
        from app.security.hashing import hash_password
        role_row = user_repository.get_role_by_name(db, role)
        user_repository.create_user(db, email=email, password_hash=hash_password(password), role_id=role_row.id)
        db.close()
    else:
        client.post("/auth/register", json={"email": email, "password": password, "role": "patient"})

    login = client.post("/auth/login", json={"email": email, "password": password})
    token = login.json()["access_token"]
    return email, token


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_sample_case(client, token, **overrides):
    payload = {
        "transplant_type": "kidney",
        "location_city": "Bengaluru",
        "location_state": "Karnataka",
        "required_services": ["Kidney transplant support"],
        "case_description": "Sample test case",
    }
    payload.update(overrides)
    return client.post("/cases", json=payload, headers=auth_headers(token))


# --- Creation ---

def test_authenticated_patient_can_create_case(client):
    _, token = register_and_login(client)
    response = create_sample_case(client, token)
    assert response.status_code == 201
    body = response.json()
    assert body["transplant_type"] == "KIDNEY"
    assert body["status"] == "NEW"


def test_unauthenticated_user_cannot_create_case(client):
    response = client.post("/cases", json={"transplant_type": "kidney"})
    assert response.status_code == 401


def test_invalid_transplant_type_rejected(client):
    _, token = register_and_login(client)
    response = create_sample_case(client, token, transplant_type="pancreas")
    assert response.status_code == 422


def test_missing_required_field_rejected(client):
    _, token = register_and_login(client)
    response = client.post("/cases", json={}, headers=auth_headers(token))
    assert response.status_code == 422


def test_non_patient_cannot_create_case(client):
    _, coordinator_token = register_and_login(client, "coord", role="coordinator")
    response = create_sample_case(client, coordinator_token)
    assert response.status_code == 403


# --- Access / ownership ---

def test_patient_can_view_own_case(client):
    _, token = register_and_login(client)
    case_id = create_sample_case(client, token).json()["id"]
    response = client.get(f"/cases/{case_id}", headers=auth_headers(token))
    assert response.status_code == 200


def test_patient_cannot_view_another_patients_case(client):
    _, token_a = register_and_login(client, "patienta")
    _, token_b = register_and_login(client, "patientb")
    case_id = create_sample_case(client, token_a).json()["id"]

    response = client.get(f"/cases/{case_id}", headers=auth_headers(token_b))
    assert response.status_code == 404  # not 403 — ownership never leaked


def test_malformed_case_id_returns_422_not_500(client):
    _, token = register_and_login(client)
    response = client.get("/cases/not-a-real-uuid", headers=auth_headers(token))
    assert response.status_code == 422


def test_coordinator_can_view_any_case(client):
    _, patient_token = register_and_login(client, "patientc")
    _, coordinator_token = register_and_login(client, "coordb", role="coordinator")
    case_id = create_sample_case(client, patient_token).json()["id"]

    response = client.get(f"/cases/{case_id}", headers=auth_headers(coordinator_token))
    assert response.status_code == 200


def test_case_list_scoped_to_own_patient(client):
    _, token_a = register_and_login(client, "lista")
    _, token_b = register_and_login(client, "listb")
    create_sample_case(client, token_a)
    create_sample_case(client, token_b)

    response = client.get("/cases", headers=auth_headers(token_a))
    assert response.status_code == 200
    assert len(response.json()) == 1


# --- Update ---

def test_owner_can_update_case_while_editable(client):
    _, token = register_and_login(client, "updatea")
    case_id = create_sample_case(client, token).json()["id"]

    response = client.patch(f"/cases/{case_id}", json={"location_city": "Chennai"}, headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["location_city"] == "Chennai"


def test_non_owner_cannot_update_case(client):
    _, token_a = register_and_login(client, "updateb")
    _, token_b = register_and_login(client, "updatec")
    case_id = create_sample_case(client, token_a).json()["id"]

    response = client.patch(f"/cases/{case_id}", json={"location_city": "Chennai"}, headers=auth_headers(token_b))
    assert response.status_code == 404


# --- Status transitions ---

def test_valid_status_transition_succeeds(client):
    coordinator_email = unique_email("coordd")
    _, token = register_and_login(client, "statusa")
    case_id = create_sample_case(client, token).json()["id"]

    # Patient's only allowed self-service transition is cancellation.
    response = client.post(f"/cases/{case_id}/status", json={"new_status": "CANCELLED", "reason": "test"}, headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["status"] == "CANCELLED"


def test_invalid_status_transition_rejected(client):
    _, token = register_and_login(client, "statusb")
    case_id = create_sample_case(client, token).json()["id"]

    # NEW -> COMPLETED skips the whole review pipeline; must be rejected.
    response = client.post(f"/cases/{case_id}/status", json={"new_status": "COMPLETED"}, headers=auth_headers(token))
    assert response.status_code == 409


def test_patient_cannot_advance_review_status(client):
    _, token = register_and_login(client, "statusc")
    case_id = create_sample_case(client, token).json()["id"]

    response = client.post(f"/cases/{case_id}/status", json={"new_status": "DOCUMENT_COLLECTION"}, headers=auth_headers(token))
    assert response.status_code == 403


def test_terminal_state_rejects_further_transitions(client):
    _, token = register_and_login(client, "statusd")
    case_id = create_sample_case(client, token).json()["id"]
    client.post(f"/cases/{case_id}/status", json={"new_status": "CANCELLED"}, headers=auth_headers(token))

    response = client.post(f"/cases/{case_id}/status", json={"new_status": "NEW"}, headers=auth_headers(token))
    assert response.status_code == 409


def test_cancelled_case_can_no_longer_be_edited(client):
    _, token = register_and_login(client, "statuse")
    case_id = create_sample_case(client, token).json()["id"]
    client.post(f"/cases/{case_id}/status", json={"new_status": "CANCELLED"}, headers=auth_headers(token))

    response = client.patch(f"/cases/{case_id}", json={"location_city": "Mumbai"}, headers=auth_headers(token))
    assert response.status_code == 409


# --- Timeline ---

def test_case_creation_seeds_timeline(client):
    _, token = register_and_login(client, "timelinea")
    case_id = create_sample_case(client, token).json()["id"]

    response = client.get(f"/cases/{case_id}/timeline", headers=auth_headers(token))
    assert response.status_code == 200
    entries = response.json()
    assert len(entries) == 1
    assert entries[0]["to_status"] == "NEW"
    assert entries[0]["from_status"] is None


def test_status_change_adds_timeline_entry_with_correct_actor(client):
    _, token = register_and_login(client, "timelineb")
    case_id = create_sample_case(client, token).json()["id"]
    client.post(f"/cases/{case_id}/status", json={"new_status": "CANCELLED", "reason": "test reason"}, headers=auth_headers(token))

    response = client.get(f"/cases/{case_id}/timeline", headers=auth_headers(token))
    entries = response.json()
    assert len(entries) == 2
    assert entries[1]["from_status"] == "NEW"
    assert entries[1]["to_status"] == "CANCELLED"
    assert entries[1]["reason"] == "test reason"


def test_timeline_not_visible_to_non_owner(client):
    _, token_a = register_and_login(client, "timelinec")
    _, token_b = register_and_login(client, "timelined")
    case_id = create_sample_case(client, token_a).json()["id"]

    response = client.get(f"/cases/{case_id}/timeline", headers=auth_headers(token_b))
    assert response.status_code == 404
