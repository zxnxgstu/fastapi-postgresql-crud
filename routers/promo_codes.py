from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
from dependencies import get_db, get_current_admin
from models import User
from schemas import PromoCodeCreate, PromoCodeResponse


router = APIRouter(
    prefix="/promo-codes",
    tags=["Promo codes"]
)


@router.post(
    "",
    response_model=PromoCodeResponse,
    status_code=201
)
def create_promo_code(
    promo_code: PromoCodeCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    existing_promo_code = crud.get_promo_code_by_code(
        db,
        promo_code.code
    )

    if existing_promo_code is not None:
        raise HTTPException(
            status_code=400,
            detail="Promo code already exists"
        )

    return crud.create_promo_code(
        db,
        promo_code
    )


@router.get(
    "/{code}",
    response_model=PromoCodeResponse
)
def get_promo_code(
    code: str,
    db: Session = Depends(get_db)
):
    promo_code = crud.get_promo_code_by_code(
        db,
        code
    )

    if promo_code is None or not promo_code.active:
        raise HTTPException(
            status_code=404,
            detail="Promo code not found"
        )

    return promo_code