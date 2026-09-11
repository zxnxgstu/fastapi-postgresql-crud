from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import crud

from dependencies import get_db, get_current_admin
from models import User
from schemas import AuditLogResponse


router = APIRouter(
    prefix="/admin/audit-logs",
    tags=["admin-audit-logs"]
)


@router.get(
    "",
    response_model=list[AuditLogResponse]
)
def get_admin_audit_logs(
    action: str | None = None,
    actor_user_id: int | None = Query(
        default=None,
        ge=1
    ),
    entity_type: str | None = None,
    entity_id: int | None = Query(
        default=None,
        ge=1
    ),
    skip: int = Query(
        default=0,
        ge=0
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return crud.get_audit_logs(
        db=db,
        action=action,
        actor_user_id=actor_user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        skip=skip,
        limit=limit
    )