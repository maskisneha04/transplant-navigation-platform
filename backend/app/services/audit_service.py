from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    action: str,
    user_id=None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    metadata: dict | None = None,
    ip_address: str | None = None,
) -> AuditLog:
    """
    Writes one audit trail row. NEVER pass document contents or clinical text
    in `metadata` — only structural/administrative facts (e.g. {"email": "..."}).
    """
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        log_metadata=metadata or {},
        timestamp=datetime.now(timezone.utc),
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
    return entry
