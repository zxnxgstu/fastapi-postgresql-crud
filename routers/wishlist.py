from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

import crud
from dependencies import get_current_user, get_db
from models import User
from schemas import WishlistItemCreate, WishlistItemResponse


router = APIRouter(
    prefix="/wishlist",
    tags=["Wishlist"]
)


@router.get(
    "",
    response_model=list[WishlistItemResponse]
)
def get_my_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_wishlist(
        db,
        current_user.id
    )


@router.post(
    "",
    response_model=WishlistItemResponse,
    status_code=201
)
def add_to_wishlist(
    item: WishlistItemCreate,
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

    existing_item = crud.get_wishlist_item(
        db,
        current_user.id,
        item.product_id
    )

    if existing_item is not None:
        raise HTTPException(
            status_code=400,
            detail="Product already in wishlist"
        )

    return crud.add_wishlist_item(
        db,
        current_user.id,
        item.product_id
    )


@router.delete(
    "/{product_id}",
    status_code=204
)
def remove_from_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    wishlist_item = crud.get_wishlist_item(
        db,
        current_user.id,
        product_id
    )

    if wishlist_item is None:
        raise HTTPException(
            status_code=404,
            detail="Wishlist item not found"
        )

    crud.delete_wishlist_item(
        db,
        wishlist_item
    )

    return Response(status_code=204)