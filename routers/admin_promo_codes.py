from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import crud

from dependencies import get_db, get_current_admin
from models import User
from schemas import PromoCodeResponse, PromoCodeUpdate


router = APIRouter(
    prefix="/admin/promo-codes",
    tags=["admin-promo-codes"]
)


@router.get(
    "",
    response_model=list[PromoCodeResponse]
)
def get_admin_promo_codes(
    active: bool | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return crud.get_promo_codes(
        db=db,
        active=active,
        skip=skip,
        limit=limit
    )


@router.patch(
    "/{promo_code_id}",
    response_model=PromoCodeResponse
)
def update_admin_promo_code(
    promo_code_id: int,
    update_data: PromoCodeUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    promo_code = crud.get_promo_code_by_id(
        db,
        promo_code_id
    )

    if promo_code is None:
        raise HTTPException(
            status_code=404,
            detail="Promo code not found"
        )

    changes = update_data.model_dump(
        exclude_unset=True
    )

    promo_code = crud.update_promo_code(
        db,
        promo_code,
        update_data
    )

    if changes:
        changed_fields = ", ".join(
            changes.keys()
        )

        crud.create_audit_log(
            db=db,
            actor_user_id=current_admin.id,
            action="promo_code_updated",
            entity_type="promo_code",
            entity_id=promo_code.id,
            details=(
                f"updated_fields: {changed_fields}"
            )
        )

    db.commit()
    db.refresh(promo_code)

    return promo_code