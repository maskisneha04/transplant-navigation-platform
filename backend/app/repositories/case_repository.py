import uuid

from sqlalchemy.orm import Session

from app.models.transplant_case import TransplantCase, CaseStatusHistory, PatientPreference
from app.models.patient import Patient


def get_patient_by_user_id(db: Session, user_id: uuid.UUID) -> Patient | None:
    return db.query(Patient).filter(Patient.user_id == user_id, Patient.deleted_at.is_(None)).first()


def get_or_create_patient_profile(db: Session, user_id: uuid.UUID) -> Patient:
    """
    Phase 1 only creates a `users` row on registration; the extended `patients`
    profile row is created lazily the first time a patient touches the case
    workflow. This keeps registration fast and avoids collecting profile data
    before it's needed.
    """
    patient = get_patient_by_user_id(db, user_id)
    if patient:
        return patient
    patient = Patient(user_id=user_id)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def create_case(db: Session, patient_id: uuid.UUID, **fields) -> TransplantCase:
    case = TransplantCase(patient_id=patient_id, **fields)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def get_case_by_id(db: Session, case_id: uuid.UUID) -> TransplantCase | None:
    return db.query(TransplantCase).filter(TransplantCase.id == case_id, TransplantCase.deleted_at.is_(None)).first()


def list_cases_for_patient(db: Session, patient_id: uuid.UUID) -> list[TransplantCase]:
    return (
        db.query(TransplantCase)
        .filter(TransplantCase.patient_id == patient_id, TransplantCase.deleted_at.is_(None))
        .order_by(TransplantCase.created_at.desc())
        .all()
    )


def list_all_cases(db: Session) -> list[TransplantCase]:
    """Coordinator/admin visibility — full list. Filtering by assignment can be layered on in a later phase."""
    return db.query(TransplantCase).filter(TransplantCase.deleted_at.is_(None)).order_by(TransplantCase.created_at.desc()).all()


def update_case_fields(db: Session, case: TransplantCase, updates: dict) -> TransplantCase:
    for key, value in updates.items():
        if value is not None:
            setattr(case, key, value)
    db.commit()
    db.refresh(case)
    return case


def add_preferences(db: Session, case_id: uuid.UUID, preferences: list[dict]) -> None:
    for pref in preferences:
        db.add(PatientPreference(case_id=case_id, preference_key=pref["preference_key"], preference_value=pref["preference_value"]))
    db.commit()


def get_preferences_for_case(db: Session, case_id: uuid.UUID) -> list[PatientPreference]:
    return db.query(PatientPreference).filter(PatientPreference.case_id == case_id).all()


def record_status_change(
    db: Session, case_id: uuid.UUID, from_status: str | None, to_status: str, changed_by: uuid.UUID, reason: str | None
) -> CaseStatusHistory:
    entry = CaseStatusHistory(case_id=case_id, from_status=from_status, to_status=to_status, changed_by=changed_by, reason=reason)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_timeline_for_case(db: Session, case_id: uuid.UUID) -> list[CaseStatusHistory]:
    return (
        db.query(CaseStatusHistory)
        .filter(CaseStatusHistory.case_id == case_id)
        .order_by(CaseStatusHistory.created_at.asc())
        .all()
    )
