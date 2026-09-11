from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import crud

from dependencies import get_db, get_current_admin
from models import User
from schemas import StockMovementResponse


router = APIRouter(
    prefix="/admin/inventory",
    tags=["admin-inventory"]
)


@router.get(
    "/movements",
    response_model=list[StockMovementResponse]
)
def get_inventory_movements(
    product_id: int | None = None,
    reason: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return crud.get_stock_movements(
        db=db,
        product_id=product_id,
        reason=reason,
        skip=skip,
        limit=limit
    )