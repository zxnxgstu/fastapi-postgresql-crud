from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

import crud
from dependencies import get_current_user, get_db
from models import User
from schemas import ReviewCreate, ReviewResponse, ReviewUpdate


router = APIRouter(
    prefix="/products",
    tags=["Reviews"]
)


@router.get(
    "/{product_id}/reviews",
    response_model=list[ReviewResponse]
)
def get_product_reviews(
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

    return crud.get_product_reviews(
        db,
        product_id
    )


@router.post(
    "/{product_id}/reviews",
    response_model=ReviewResponse,
    status_code=201
)
def create_product_review(
    product_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    existing_review = crud.get_user_review_for_product(
        db,
        current_user.id,
        product_id
    )

    if existing_review is not None:
        raise HTTPException(
            status_code=400,
            detail="You already reviewed this product"
        )

    return crud.create_review(
        db,
        current_user.id,
        product_id,
        review_data
    )


@router.patch(
    "/reviews/{review_id}",
    response_model=ReviewResponse
)
def update_my_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = crud.get_review(
        db,
        review_id
    )

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot edit this review"
        )

    return crud.update_review(
        db,
        review,
        review_data
    )


@router.delete(
    "/reviews/{review_id}",
    status_code=204
)
def delete_my_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    review = crud.get_review(
        db,
        review_id
    )

    if review is None:
        raise HTTPException(
            status_code=404,
            detail="Review not found"
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot delete this review"
        )

    crud.delete_review(
        db,
        review
    )

    return Response(status_code=204)