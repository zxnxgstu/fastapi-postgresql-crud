from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
from dependencies import get_db, get_current_admin
from models import User
from schemas import CategoryCreate, CategoryResponse


router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


@router.get("", response_model=list[CategoryResponse])
def get_categories(
    db: Session = Depends(get_db)
):
    return crud.get_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = crud.get_category(db, category_id)

    if category is None:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    existing_category = crud.get_category_by_name(
        db,
        category.name
    )

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    return crud.create_category(db, category)