from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Literal
import crud
from dependencies import get_db, get_current_admin, get_current_user
from models import User
from schemas import OrderCreate, OrderResponse, OrderStatusUpdate


router = APIRouter(
    tags=["orders"]
)


@router.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        order = crud.create_order_from_cart(
            db,
            current_user.id,
            order_data
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Not enough stock"
        )

    if order is None:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    return order


@router.get("/orders", response_model=list[OrderResponse])
def get_my_orders(
    status: Literal[
        "pending",
        "paid",
        "shipped",
        "completed",
        "cancelled"
    ] | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_user_orders(
        db,
        current_user.id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_my_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = crud.get_user_order(
        db,
        order_id,
        current_user.id
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


@router.get("/admin/orders", response_model=list[OrderResponse])
def get_all_orders(
    status: Literal[
        "pending",
        "paid",
        "shipped",
        "completed",
        "cancelled"
    ] | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return crud.get_all_orders(
        db,
        status=status,
        skip=skip,
        limit=limit
    )


@router.patch(
    "/admin/orders/{order_id}/status",
    response_model=OrderResponse
)
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    order = crud.get_order(
        db,
        order_id
    )

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return crud.update_order_status(
        db,
        order,
        status_data
    )