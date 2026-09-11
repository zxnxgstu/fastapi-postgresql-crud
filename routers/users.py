from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_
from typing import Literal
import crud
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from dependencies import get_db, get_current_user, get_current_admin
from models import User
from schemas import (
    UserCreate,
    UserResponse,
    Token,
    RefreshTokenRequest,
    RefreshSessionResponse,
    UserRoleUpdate,
    UserPasswordChange,
    UserActiveUpdate,
    UserProfileUpdate,
)


router = APIRouter(
    tags=["users"]
)


@router.post("/register", response_model=UserResponse, status_code=201)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_username = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )

    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    existing_email = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    if not user.is_active:
        raise HTTPException(
        status_code=403,
        detail="Account is disabled"
    )

    access_token = create_access_token(
        data={"sub": str(user.id)}
)

    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
)
    refresh_payload = decode_refresh_token(
        refresh_token
    )

    expires_at = datetime.fromtimestamp(
        refresh_payload["exp"],
        tz=timezone.utc
    )

    crud.create_refresh_token_session(
        db=db,
        user_id=user.id,
        jti=refresh_payload["jti"],
        expires_at=expires_at
    )

    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    payload = decode_refresh_token(
        token_data.refresh_token
    )

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    user_id_raw = payload.get("sub")
    jti = payload.get("jti")

    if user_id_raw is None or jti is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    refresh_session = crud.get_refresh_token_session(
        db,
        jti
    )

    if (
        refresh_session is None
        or refresh_session.revoked
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    crud.revoke_refresh_token_session(
        refresh_session
    )

    access_token = create_access_token(
        data={
            "sub": str(user.id)
        }
    )

    new_refresh_token = create_refresh_token(
        data={
            "sub": str(user.id)
        }
    )

    new_payload = decode_refresh_token(
        new_refresh_token
    )

    if new_payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    new_expires_at = datetime.fromtimestamp(
        new_payload["exp"],
        tz=timezone.utc
    )

    crud.create_refresh_token_session(
        db=db,
        user_id=user.id,
        jti=new_payload["jti"],
        expires_at=new_expires_at
    )

    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout", status_code=204)
def logout(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    payload = decode_refresh_token(
        token_data.refresh_token
    )

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    jti = payload.get("jti")

    if jti is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    refresh_session = crud.get_refresh_token_session(
        db,
        jti
    )

    if (
        refresh_session is None
        or refresh_session.revoked
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    crud.revoke_refresh_token_session(
        refresh_session
    )

    db.commit()

    return Response(status_code=204)

@router.post("/logout-all", status_code=204)
def logout_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    crud.revoke_all_user_refresh_tokens(
        db=db,
        user_id=current_user.id
    )

    db.commit()

    return Response(status_code=204)

@router.get(
    "/sessions",
    response_model=list[RefreshSessionResponse]
)
def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud.get_user_refresh_sessions(
        db=db,
        user_id=current_user.id
    )


@router.delete(
    "/sessions/{session_id}",
    status_code=204
)
def revoke_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    refresh_session = crud.get_user_refresh_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id
    )

    if (
        refresh_session is None
        or refresh_session.revoked
    ):
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    crud.revoke_refresh_token_session(
        refresh_session
    )

    db.commit()

    return Response(status_code=204)

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.patch(
    "/me",
    response_model=UserResponse
)
def update_me(
    update_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return crud.update_user_profile(
            db=db,
            user=current_user,
            update_data=update_data
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

@router.patch("/me/password", status_code=204)
def change_password(
    password_data: UserPasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(
        password_data.current_password,
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )

    if verify_password(
        password_data.new_password,
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=400,
            detail="New password must be different"
        )

    current_user.hashed_password = hash_password(
        password_data.new_password
    )

    crud.revoke_all_user_refresh_tokens(
        db=db,
        user_id=current_user.id
    )

    db.commit()

    return Response(status_code=204)

@router.get(
    "/users",
    response_model=list[UserResponse]
)
def get_users(
    search: str | None = None,
    role: Literal["user", "admin"] | None = None,
    active: bool | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    query = db.query(User)

    if search:
        query = query.filter(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    if role is not None:
        query = query.filter(
            User.role == role
        )

    if active is not None:
        query = query.filter(
            User.is_active == active
        )

    return (
        query
        .order_by(User.id.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

@router.patch(
    "/users/{user_id}/role",
    response_model=UserResponse
)
def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    old_role = user.role
    new_role = role_data.role

    user.role = new_role

    if old_role != new_role:
        crud.create_audit_log(
            db=db,
            actor_user_id=current_admin.id,
            action="user_role_changed",
            entity_type="user",
            entity_id=user.id,
            details=f"role: {old_role} -> {new_role}"
        )

    db.commit()
    db.refresh(user)

    return user

@router.patch(
    "/users/{user_id}/active",
    response_model=UserResponse
)
def update_user_active_status(
    user_id: int,
    active_data: UserActiveUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    old_status = user.is_active
    new_status = active_data.is_active

    user.is_active = new_status

    if old_status != new_status:
        action = (
            "user_activated"
            if new_status
            else "user_deactivated"
        )

        crud.create_audit_log(
            db=db,
            actor_user_id=current_admin.id,
            action=action,
            entity_type="user",
            entity_id=user.id,
            details=(
                f"is_active: {old_status} -> {new_status}"
            )
        )

    if not new_status:
        crud.revoke_all_user_refresh_tokens(
            db=db,
            user_id=user.id
        )

    db.commit()
    db.refresh(user)

    return user