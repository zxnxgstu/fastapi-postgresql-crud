from sqlalchemy.orm import Session

from models import Review
from schemas import ReviewCreate, ReviewUpdate


def get_product_reviews(
    db: Session,
    product_id: int
):
    return (
        db.query(Review)
        .filter(Review.product_id == product_id)
        .order_by(Review.id.desc())
        .all()
    )


def get_review(
    db: Session,
    review_id: int
):
    return (
        db.query(Review)
        .filter(Review.id == review_id)
        .first()
    )


def get_user_review_for_product(
    db: Session,
    user_id: int,
    product_id: int
):
    return (
        db.query(Review)
        .filter(
            Review.user_id == user_id,
            Review.product_id == product_id
        )
        .first()
    )


def create_review(
    db: Session,
    user_id: int,
    product_id: int,
    review_data: ReviewCreate
):
    review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=review_data.rating,
        comment=review_data.comment
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


def update_review(
    db: Session,
    review: Review,
    review_data: ReviewUpdate
):
    review.rating = review_data.rating
    review.comment = review_data.comment

    db.commit()
    db.refresh(review)

    return review


def delete_review(
    db: Session,
    review: Review
):
    db.delete(review)
    db.commit()