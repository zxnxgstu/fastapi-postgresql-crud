from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Order, Product, User


def get_admin_stats(db: Session):
    total_users = (
        db.query(func.count(User.id))
        .scalar()
    )

    total_products = (
        db.query(func.count(Product.id))
        .scalar()
    )

    total_orders = (
        db.query(func.count(Order.id))
        .scalar()
    )

    completed_orders = (
        db.query(func.count(Order.id))
        .filter(Order.status == "completed")
        .scalar()
    )

    total_revenue = (
        db.query(func.coalesce(func.sum(Order.total_price), 0))
        .filter(Order.status == "completed")
        .scalar()
    )

    return {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "total_revenue": total_revenue,
    }