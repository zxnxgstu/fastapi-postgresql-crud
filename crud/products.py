from sqlalchemy.orm import Session

from models import Product
from schemas import ProductCreate


def get_products(
    db: Session,
    search: str | None = None,
    in_stock: bool | None = None,
    skip: int = 0,
    limit: int = 10
):
    query = db.query(Product)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if in_stock is not None:
        query = query.filter(Product.in_stock == in_stock)

    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    return (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )


def create_product(db: Session, product: ProductCreate):
    db_product = Product(
        name=product.name,
        price=product.price,
        in_stock=product.in_stock
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


def update_product(
    db: Session,
    product_id: int,
    updated_product: ProductCreate
):
    db_product = get_product(db, product_id)

    if db_product is None:
        return None

    db_product.name = updated_product.name
    db_product.price = updated_product.price
    db_product.in_stock = updated_product.in_stock

    db.commit()
    db.refresh(db_product)

    return db_product


def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)

    if db_product is None:
        return False

    db.delete(db_product)
    db.commit()

    return True