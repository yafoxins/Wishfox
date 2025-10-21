from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.utils.security import get_current_user
from app.utils.seeder import seed

router = APIRouter()


@router.post("/debug/seed", status_code=status.HTTP_202_ACCEPTED)
def trigger_seed(_: str = Depends(get_current_user)) -> dict[str, str]:
    if settings.is_prod:
        raise HTTPException(status_code=403, detail="Seed endpoint disabled in production")
    seed()
    return {"detail": "Seed data created"}
