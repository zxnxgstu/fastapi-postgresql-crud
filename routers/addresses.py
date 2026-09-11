from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
from dependencies import get_current_user, get_db
from models import User
from schemas import (
    AddressCreate,
    AddressResponse,
    AddressUpdate,
)


router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"]
)


@router.get(
    "",
    response_model=list[AddressResponse]
)
def get_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_user_addresses(
        db,
        current_user.id
    )


@router.post(
    "",
    response_model=AddressResponse,
    status_code=201
)
def create_address(
    address_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.create_address(
        db,
        current_user.id,
        address_data
    )


@router.patch(
    "/{address_id}",
    response_model=AddressResponse
)
def update_address(
    address_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    address = crud.get_user_address(
        db,
        address_id,
        current_user.id
    )

    if address is None:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    return crud.update_address(
        db,
        address,
        address_data
    )


@router.delete(
    "/{address_id}",
    status_code=204
)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    address = crud.get_user_address(
        db,
        address_id,
        current_user.id
    )

    if address is None:
        raise HTTPException(
            status_code=404,
            detail="Address not found"
        )

    crud.delete_address(
        db,
        address
    )