from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Literal

import crud

from dependencies import get_db, get_current_admin
from models import User
from schemas import ProductResponse


router = APIRouter(
    prefix="/admin/products",
    tags=["admin-products"]
)


@router.get(
    "",
    response_model=list[ProductResponse]
)
def get_admin_products(
    active: bool | None = None,
    search: str | None = None,
    in_stock: bool | None = None,
    category_id: int | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    sort_by: Literal[
        "id",
        "name",
        "price",
        "stock_quantity"
    ] = "id",
    order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return crud.get_products(
        db=db,
        search=search,
        in_stock=in_stock,
        category_id=category_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order,
        active=active
    )