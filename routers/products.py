from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

import crud
from dependencies import get_db, get_current_user
from models import User
from schemas import ProductCreate, ProductResponse


router = APIRouter(
    prefix="/products",
    tags=["products"]
)


@router.get("", response_model=list[ProductResponse])
def get_products(
    search: str | None = None,
    in_stock: bool | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return crud.get_products(
        db,
        search=search,
        in_stock=in_stock,
        skip=skip,
        limit=limit
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
    return crud.create_product(db, product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    updated_product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
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
    current_user: User = Depends(get_current_user)
):
    deleted = crud.delete_product(db, product_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return Response(status_code=204)