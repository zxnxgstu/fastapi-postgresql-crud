from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import date, timedelta
from models import Order, OrderItem, Product, User


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

def get_top_products(
    db: Session,
    limit: int = 5
):
    rows = (
        db.query(
            OrderItem.product_id.label("product_id"),
            OrderItem.product_name.label("product_name"),
            func.sum(OrderItem.quantity).label("units_sold"),
            func.sum(OrderItem.line_total).label("revenue"),
        )
        .join(
            Order,
            Order.id == OrderItem.order_id
        )
        .filter(
            Order.status == "completed"
        )
        .group_by(
            OrderItem.product_id,
            OrderItem.product_name
        )
        .order_by(
            func.sum(OrderItem.quantity).desc(),
            func.sum(OrderItem.line_total).desc()
        )
        .limit(limit)
        .all()
    )

    return [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "units_sold": row.units_sold,
            "revenue": row.revenue,
        }
        for row in rows
    ]

def get_sales_by_day(
    db: Session,
    days: int = 7
):
    start_date = date.today() - timedelta(days=days - 1)

    delivery_date = func.date(Order.delivered_at)

    rows = (
        db.query(
            delivery_date.label("date"),
            func.count(Order.id).label("orders"),
            func.sum(Order.total_price).label("revenue"),
        )
        .filter(
            Order.status == "completed",
            Order.delivered_at.is_not(None),
            delivery_date >= start_date
        )
        .group_by(delivery_date)
        .order_by(delivery_date.asc())
        .all()
    )

    return [
        {
            "date": row.date,
            "orders": row.orders,
            "revenue": row.revenue,
        }
        for row in rows
    ]

def get_orders_by_status(db: Session):
    rows = (
        db.query(
            Order.status.label("status"),
            func.count(Order.id).label("orders"),
        )
        .group_by(Order.status)
        .order_by(Order.status.asc())
        .all()
    )

    return [
        {
            "status": row.status,
            "orders": row.orders,
        }
        for row in rows
    ]