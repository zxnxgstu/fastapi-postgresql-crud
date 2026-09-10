from sqlalchemy.orm import Session
from models import Product
from schemas import ProductCreate


def get_products(db: Session):
    return db.query(Product).all()


def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def create_product(db: Session, product: ProductCreate):
    new_product = Product(
        name=product.name,
        price=product.price,
        in_stock=product.in_stock
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


def update_product(db: Session, product_id: int, updated_product: ProductCreate):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        return None

    product.name = updated_product.name
    product.price = updated_product.price
    product.in_stock = updated_product.in_stock

    db.commit()
    db.refresh(product)

    return product


def delete_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        return None

    db.delete(product)
    db.commit()

    return product