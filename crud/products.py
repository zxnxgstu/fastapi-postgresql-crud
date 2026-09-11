from sqlalchemy.orm import Session

from models import Product
from schemas import ProductCreate


def get_products(
    db: Session,
    search: str | None = None,
    in_stock: bool | None = None,
    category_id: int | None = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "id",
    order: str = "asc"
):
    query = db.query(Product)

    if search:
        query = query.filter(
            Product.name.ilike(f"%{search}%")
        )

    if in_stock is not None:
        query = query.filter(
            Product.in_stock == in_stock
        )

    if category_id is not None:
        query = query.filter(
            Product.category_id == category_id
        )

    sort_columns = {
        "id": Product.id,
        "name": Product.name,
        "price": Product.price,
        "stock_quantity": Product.stock_quantity
    }

    sort_column = sort_columns.get(
        sort_by,
        Product.id
    )

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
    return (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )


def create_product(db: Session, product: ProductCreate):
    stock_quantity = product.stock_quantity

    if stock_quantity is None:
        stock_quantity = 1 if product.in_stock else 0

    db_product = Product(
        name=product.name,
        price=product.price,
        in_stock=stock_quantity > 0,
        stock_quantity=stock_quantity,
        category_id=product.category_id
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

    stock_quantity = updated_product.stock_quantity

    if stock_quantity is None:
        stock_quantity = db_product.stock_quantity

        if updated_product.in_stock is False:
            stock_quantity = 0
        elif updated_product.in_stock is True and stock_quantity == 0:
            stock_quantity = 1

    db_product.name = updated_product.name
    db_product.price = updated_product.price
    db_product.stock_quantity = stock_quantity
    db_product.in_stock = stock_quantity > 0
    db_product.category_id = updated_product.category_id

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