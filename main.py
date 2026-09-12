from fastapi import FastAPI
from routers.cart import router as cart_router
from dependencies import get_db
from routers.products import router as products_router
from routers.users import router as users_router
from routers.categories import router as categories_router
from routers.orders import router as orders_router
from routers.promo_codes import router as promo_codes_router
from routers.wishlist import router as wishlist_router
from routers.reviews import router as reviews_router
from routers.notifications import router as notifications_router
from routers.addresses import router as addresses_router
from routers.delivery_methods import router as delivery_methods_router
from routers.inventory import router as inventory_router
from routers.admin_products import router as admin_products_router
from routers.admin_promo_codes import router as admin_promo_codes_router
from routers.admin_audit_logs import router as admin_audit_logs_router
from routers.health import router as health_router

app = FastAPI(
    title="E-Commerce REST API",
    description=(
        "Backend API for an e-commerce platform built with "
        "FastAPI, PostgreSQL, SQLAlchemy and JWT authentication."
    ),
    version="1.0.2"
)

app.include_router(products_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(promo_codes_router)
app.include_router(wishlist_router)
app.include_router(reviews_router)
app.include_router(notifications_router)
app.include_router(addresses_router)
app.include_router(delivery_methods_router)
app.include_router(inventory_router)
app.include_router(admin_products_router)
app.include_router(admin_promo_codes_router)
app.include_router(admin_audit_logs_router)
app.include_router(health_router)

@app.get("/")
def home():
    return {"message": "Hello from FastAPI"}