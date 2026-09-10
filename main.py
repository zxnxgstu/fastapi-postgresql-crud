from fastapi import FastAPI, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from schemas import ProductCreate, ProductResponse
from database import SessionLocal
from models import Product
import crud


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Hello from FastAPI"}


@app.get("/products", response_model=list[ProductResponse])
def get_products(
    search: str | None = None,
    in_stock: bool | None = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return crud.get_products(
        db,
        search=search,
        in_stock=in_stock,
        skip=skip,
        limit=limit
    )


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product(db, product_id)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db, product)


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    updated_product: ProductCreate,
    db: Session = Depends(get_db)
):
    product = crud.update_product(db, product_id, updated_product)

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_product(db, product_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return Response(status_code=204)
