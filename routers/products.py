from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session
from typing import Literal
import crud
from dependencies import get_db, get_current_user, get_current_admin
from models import User
from schemas import (
    ProductCreate,
    ProductResponse,
    PriceHistoryResponse,
    StockMovementResponse,
)


router = APIRouter(
    prefix="/products",
    tags=["products"]
)


@router.get("", response_model=list[ProductResponse])
def get_products(
    search: str | None = None,
    in_stock: bool | None = None,
    category_id: int | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    sort_by: Literal["id", "name", "price", "stock_quantity"] = "id",
    order: Literal["asc", "desc"] = "asc",
    db: Session = Depends(get_db)
):
    return crud.get_products(
        db,
        search=search,
        in_stock=in_stock,
        category_id=category_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order
    )

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = crud.get_product(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if product.category_id is not None:
        category = crud.get_category(
            db,
            product.category_id
        )

        if category is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

    return crud.create_product(db, product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    updated_product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if updated_product.category_id is not None:
        category = crud.get_category(
            db,
            updated_product.category_id
        )

        if category is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

    product = crud.update_product(
        db,
        product_id,
        updated_product
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    deleted = crud.delete_product(db, product_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return Response(status_code=204)

@router.get(
    "/{product_id}/price-history",
    response_model=list[PriceHistoryResponse]
)
def get_price_history(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = crud.get_product(
        db,
        product_id
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return crud.get_product_price_history(
        db,
        product_id
    )

@router.get(
    "/{product_id}/stock-movements",
    response_model=list[StockMovementResponse]
)
def get_product_stock_history(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    product = crud.get_product(
        db,
        product_id
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return crud.get_product_stock_movements(
        db,
        product_id
    )