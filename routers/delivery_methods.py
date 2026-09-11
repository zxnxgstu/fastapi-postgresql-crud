from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
from dependencies import get_current_admin, get_db
from schemas import (
    DeliveryMethodCreate,
    DeliveryMethodResponse,
    DeliveryMethodUpdate,
)


router = APIRouter(
    prefix="/delivery-methods",
    tags=["Delivery methods"]
)


@router.get(
    "",
    response_model=list[DeliveryMethodResponse]
)
def get_delivery_methods(
    db: Session = Depends(get_db)
):
    return crud.get_active_delivery_methods(db)


@router.get(
    "/admin",
    response_model=list[DeliveryMethodResponse]
)
def get_all_delivery_methods(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    return crud.get_all_delivery_methods(db)


@router.post(
    "",
    response_model=DeliveryMethodResponse,
    status_code=201
)
def create_delivery_method(
    delivery_data: DeliveryMethodCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    existing_method = crud.get_delivery_method_by_code(
        db,
        delivery_data.code
    )

    if existing_method is not None:
        raise HTTPException(
            status_code=400,
            detail="Delivery method already exists"
        )

    return crud.create_delivery_method(
        db,
        delivery_data
    )


@router.patch(
    "/{delivery_method_id}",
    response_model=DeliveryMethodResponse
)
def update_delivery_method(
    delivery_method_id: int,
    delivery_data: DeliveryMethodUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    delivery_method = crud.get_delivery_method(
        db,
        delivery_method_id
    )

    if delivery_method is None:
        raise HTTPException(
            status_code=404,
            detail="Delivery method not found"
        )

    return crud.update_delivery_method(
        db,
        delivery_method,
        delivery_data
    )