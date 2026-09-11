from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from dependencies import get_db


router = APIRouter(
    tags=["health"]
)


@router.get("/health")
def health_check(
    db: Session = Depends(get_db)
):
    try:
        db.execute(
            text("SELECT 1")
        )

        return {
            "status": "ok",
            "database": "ok"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )