from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

import crud
from dependencies import get_db, get_current_user
from models import User
from schemas import (
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse,
)


router = APIRouter(
    prefix="/cart",
    tags=["cart"]
)


@router.get("", response_model=list[CartItemResponse])
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_cart(
        db,
        current_user.id
    )


@router.post("", response_model=CartItemResponse, status_code=201)
def add_cart_item(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = crud.get_product(
        db,
        item.product_id
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing_item = crud.get_cart_item_by_product(
        db,
        current_user.id,
        item.product_id
    )

    current_quantity = (
        existing_item.quantity
        if existing_item
        else 0
    )

    requested_quantity = (
        current_quantity + item.quantity
    )

    if requested_quantity > product.stock_quantity:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock"
        )

    return crud.add_cart_item(
        db,
        current_user.id,
        item
    )


@router.patch("/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    item: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = crud.get_cart_item(
        db,
        item_id,
        current_user.id
    )

    if cart_item is None:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    return crud.update_cart_item(
        db,
        cart_item,
        item
    )


@router.delete("/{item_id}", status_code=204)
def delete_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = crud.get_cart_item(
        db,
        item_id,
        current_user.id
    )

    if cart_item is None:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found"
        )

    crud.delete_cart_item(
        db,
        cart_item
    )

    return Response(status_code=204)