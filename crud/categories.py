from sqlalchemy.orm import Session

from models import Category
from schemas import CategoryCreate


def get_categories(db: Session):
    return db.query(Category).all()


def get_category(db: Session, category_id: int):
    return (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )


def get_category_by_name(db: Session, name: str):
    return (
        db.query(Category)
        .filter(Category.name == name)
        .first()
    )


def create_category(
    db: Session,
    category: CategoryCreate
):
    db_category = Category(
        name=category.name
    )

    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category