from sqlalchemy.orm import Session

from models import AuditLog


def create_audit_log(
    db: Session,
    actor_user_id: int | None,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    details: str | None = None
):
    audit_log = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )

    db.add(audit_log)

    return audit_log


def get_audit_logs(
    db: Session,
    action: str | None = None,
    actor_user_id: int | None = None,
    entity_type: str | None = None,
    entity_id: int | None = None,
    skip: int = 0,
    limit: int = 50
):
    query = db.query(AuditLog)

    if action is not None:
        query = query.filter(
            AuditLog.action == action
        )

    if actor_user_id is not None:
        query = query.filter(
            AuditLog.actor_user_id == actor_user_id
        )

    if entity_type is not None:
        query = query.filter(
            AuditLog.entity_type == entity_type
        )

    if entity_id is not None:
        query = query.filter(
            AuditLog.entity_id == entity_id
        )

    return (
        query
        .order_by(
            AuditLog.created_at.desc(),
            AuditLog.id.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )