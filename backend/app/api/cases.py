import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.case import (
    CaseCreateRequest,
    CaseUpdateRequest,
    StatusTransitionRequest,
    CaseResponse,
    CaseListItemResponse,
    CaseTimelineEntryResponse,
)
from app.services import case_service

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("", response_model=CaseResponse, status_code=201)
def create_case(payload: CaseCreateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    case = case_service.create_case(db, user, payload.model_dump())
    return CaseResponse.model_validate(case)


@router.get("", response_model=list[CaseListItemResponse])
def list_cases(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    cases = case_service.list_cases(db, user)
    return [CaseListItemResponse.model_validate(c) for c in cases]


@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    case = case_service.get_case(db, user, case_id)
    return CaseResponse.model_validate(case)


@router.patch("/{case_id}", response_model=CaseResponse)
def update_case(case_id: uuid.UUID, payload: CaseUpdateRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    case = case_service.update_case(db, user, case_id, payload.model_dump(exclude_unset=True))
    return CaseResponse.model_validate(case)


@router.post("/{case_id}/status", response_model=CaseResponse)
def change_status(case_id: uuid.UUID, payload: StatusTransitionRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    case = case_service.transition_status(db, user, case_id, payload.new_status, payload.reason)
    return CaseResponse.model_validate(case)


@router.get("/{case_id}/timeline", response_model=list[CaseTimelineEntryResponse])
def get_timeline(case_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entries = case_service.get_timeline(db, user, case_id)
    return [CaseTimelineEntryResponse.model_validate(e) for e in entries]
