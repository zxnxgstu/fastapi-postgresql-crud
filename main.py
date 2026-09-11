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

app = FastAPI(
    title="FastAPI PostgreSQL CRUD API"
)

app.include_router(products_router)
app.include_router(users_router)
app.include_router(categories_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(promo_codes_router)
app.include_router(wishlist_router)
app.include_router(reviews_router)

@app.get("/")
def home():
    return {"message": "Hello from FastAPI"}