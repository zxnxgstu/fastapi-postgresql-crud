from fastapi import FastAPI

from dependencies import get_db
from routers.products import router as products_router
from routers.users import router as users_router


app = FastAPI(
    title="FastAPI PostgreSQL CRUD API"
)

app.include_router(products_router)
app.include_router(users_router)


@app.get("/")
def home():
    return {"message": "Hello from FastAPI"}