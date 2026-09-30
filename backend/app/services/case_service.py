import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.transplant_case import CaseStatus, TransplantCase
from app.models.user import User
from app.repositories import case_repository
from app.services import audit_service


# ---------------------------------------------------------------------------
# Controlled state machine. Centralized here per the architecture rule that
# no route or frontend code may set `case.status` directly.
# ---------------------------------------------------------------------------
ALLOWED_TRANSITIONS: dict[CaseStatus, set[CaseStatus]] = {
    CaseStatus.NEW: {CaseStatus.DOCUMENT_COLLECTION, CaseStatus.CANCELLED},
    CaseStatus.DOCUMENT_COLLECTION: {CaseStatus.UNDER_REVIEW, CaseStatus.CANCELLED},
    CaseStatus.UNDER_REVIEW: {CaseStatus.COORDINATOR_REVIEW, CaseStatus.DOCUMENT_COLLECTION, CaseStatus.CANCELLED},
    CaseStatus.COORDINATOR_REVIEW: {CaseStatus.CENTRE_REVIEW, CaseStatus.DOCUMENT_COLLECTION, CaseStatus.CANCELLED},
    CaseStatus.CENTRE_REVIEW: {CaseStatus.COMPLETED, CaseStatus.COORDINATOR_REVIEW, CaseStatus.CANCELLED},
    CaseStatus.COMPLETED: set(),
    CaseStatus.CANCELLED: set(),
}

# Statuses during which a patient may still edit their own case details.
PATIENT_EDITABLE_STATUSES = {CaseStatus.NEW, CaseStatus.DOCUMENT_COLLECTION}


def _require_patient_profile(db: Session, user: User):
    return case_repository.get_or_create_patient_profile(db, user.id)


def _assert_can_access_case(db: Session, case: TransplantCase, user: User) -> None:
    """
    Server-side ownership check. NEVER trust a patient_id/case ownership claim
    from the frontend — this is the actual authorization boundary.
    """
    role = user.role.name.value
    if role == "patient":
        patient = case_repository.get_patient_by_user_id(db, user.id)
        if not patient or case.patient_id != patient.id:
            # 404, not 403 — do not reveal that a case with this ID exists to a non-owner.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")
    elif role in {"coordinator", "hospital_admin", "system_admin"}:
        return  # Full visibility for now; assignment-scoped filtering is a later-phase refinement.
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this case.")


def create_case(db: Session, user: User, payload: dict) -> TransplantCase:
    if user.role.name.value != "patient":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only patients can create transplant cases.")

    patient = _require_patient_profile(db, user)
    preferences = payload.pop("preferences", None) or []

    case = case_repository.create_case(
        db,
        patient_id=patient.id,
        transplant_type=payload["transplant_type"],
        location_city=payload.get("location_city"),
        location_state=payload.get("location_state"),
        preferred_region=payload.get("preferred_region"),
        required_services=payload.get("required_services"),
        logistics_preferences=payload.get("logistics_preferences"),
        case_description=payload.get("case_description"),
    )

    if preferences:
        case_repository.add_preferences(db, case.id, preferences)

    # Seed the timeline with the initial NEW status so the history is never empty.
    case_repository.record_status_change(db, case.id, from_status=None, to_status=CaseStatus.NEW.value, changed_by=user.id, reason=None)

    audit_service.log_action(db, action="CASE_CREATED", user_id=user.id, entity_type="transplant_case", entity_id=case.id, metadata={"transplant_type": case.transplant_type.value})
    return case


def get_case(db: Session, user: User, case_id: uuid.UUID) -> TransplantCase:
    case = case_repository.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")
    _assert_can_access_case(db, case, user)
    audit_service.log_action(db, action="CASE_VIEWED", user_id=user.id, entity_type="transplant_case", entity_id=case.id)
    return case


def list_cases(db: Session, user: User) -> list[TransplantCase]:
    role = user.role.name.value
    if role == "patient":
        patient = case_repository.get_patient_by_user_id(db, user.id)
        if not patient:
            return []
        return case_repository.list_cases_for_patient(db, patient.id)
    elif role in {"coordinator", "hospital_admin", "system_admin"}:
        return case_repository.list_all_cases(db)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view cases.")


def update_case(db: Session, user: User, case_id: uuid.UUID, updates: dict) -> TransplantCase:
    case = case_repository.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")
    _assert_can_access_case(db, case, user)

    role = user.role.name.value
    if role == "patient":
        if case.status not in PATIENT_EDITABLE_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This case can no longer be edited because it has moved past the initial review stage.",
            )

    updated = case_repository.update_case_fields(db, case, updates)
    audit_service.log_action(db, action="CASE_UPDATED", user_id=user.id, entity_type="transplant_case", entity_id=case.id, metadata={"fields": list(updates.keys())})
    return updated


def transition_status(db: Session, user: User, case_id: uuid.UUID, new_status_raw: str, reason: str | None) -> TransplantCase:
    case = case_repository.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")
    _assert_can_access_case(db, case, user)

    try:
        new_status = CaseStatus(new_status_raw.upper())
    except ValueError:
        allowed = ", ".join(s.value for s in CaseStatus)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown status. Must be one of: {allowed}")

    current_status = case.status
    allowed_next = ALLOWED_TRANSITIONS.get(current_status, set())
    if new_status not in allowed_next:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot move a case from {current_status.value} to {new_status.value}.",
        )

    # Patients may only cancel their own case — all other transitions belong to coordinators
    # (fully enforced once the coordinator dashboard ships; for now this keeps the boundary honest).
    role = user.role.name.value
    if role == "patient" and new_status != CaseStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patients may only cancel a case, not advance its review status.")

    case.status = new_status
    case.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(case)

    case_repository.record_status_change(db, case.id, from_status=current_status.value, to_status=new_status.value, changed_by=user.id, reason=reason)
    audit_service.log_action(
        db, action="STATUS_CHANGED", user_id=user.id, entity_type="transplant_case", entity_id=case.id,
        metadata={"from": current_status.value, "to": new_status.value, "reason": reason},
    )
    return case


def get_timeline(db: Session, user: User, case_id: uuid.UUID):
    case = case_repository.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")
    _assert_can_access_case(db, case, user)
    return case_repository.get_timeline_for_case(db, case_id)
