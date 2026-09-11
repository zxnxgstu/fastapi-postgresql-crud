from sqlalchemy.orm import Session

from models import Address
from schemas import AddressCreate, AddressUpdate


def get_user_addresses(
    db: Session,
    user_id: int
):
    return (
        db.query(Address)
        .filter(Address.user_id == user_id)
        .order_by(
            Address.is_default.desc(),
            Address.id.asc()
        )
        .all()
    )


def get_user_address(
    db: Session,
    address_id: int,
    user_id: int
):
    return (
        db.query(Address)
        .filter(
            Address.id == address_id,
            Address.user_id == user_id
        )
        .first()
    )


def unset_default_addresses(
    db: Session,
    user_id: int
):
    (
        db.query(Address)
        .filter(
            Address.user_id == user_id,
            Address.is_default.is_(True)
        )
        .update(
            {"is_default": False},
            synchronize_session=False
        )
    )


def create_address(
    db: Session,
    user_id: int,
    address_data: AddressCreate
):
    existing_addresses = (
        db.query(Address)
        .filter(Address.user_id == user_id)
        .count()
    )

    make_default = (
        address_data.is_default
        or existing_addresses == 0
    )

    if make_default:
        unset_default_addresses(
            db,
            user_id
        )

    address = Address(
        user_id=user_id,
        city=address_data.city,
        street=address_data.street,
        postal_code=address_data.postal_code,
        is_default=make_default
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    return address


def update_address(
    db: Session,
    address: Address,
    address_data: AddressUpdate
):
    if address_data.is_default:
        unset_default_addresses(
            db,
            address.user_id
        )

    address.city = address_data.city
    address.street = address_data.street
    address.postal_code = address_data.postal_code
    address.is_default = address_data.is_default

    db.commit()
    db.refresh(address)

    return address


def delete_address(
    db: Session,
    address: Address
):
    was_default = address.is_default
    user_id = address.user_id

    db.delete(address)
    db.flush()

    if was_default:
        next_address = (
            db.query(Address)
            .filter(Address.user_id == user_id)
            .order_by(Address.id.asc())
            .first()
        )

        if next_address is not None:
            next_address.is_default = True

    db.commit()