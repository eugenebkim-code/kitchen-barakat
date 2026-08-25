from fastapi import APIRouter, Depends
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.security import get_current_tg_user
from app.core.config import settings
from app.models.all_models import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/telegram")
async def telegram_auth(
    current_tg_user: Dict[str, Any] = Depends(get_current_tg_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Validates Telegram WebApp initData HMAC and returns profile context with store settings.
    Upserts user record in DB.
    """
    stmt = select(User).where(User.telegram_id == current_tg_user["telegram_id"])
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=current_tg_user["telegram_id"],
            username=current_tg_user.get("username"),
            first_name=current_tg_user.get("first_name"),
            last_name=current_tg_user.get("last_name"),
            is_admin=current_tg_user.get("is_admin", False)
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return {
        "user": current_tg_user,
        "settings": {
            "is_open": True,
            "delivery_fee": settings.DEFAULT_DELIVERY_FEE,
            "bank_details": {
                "bank": settings.BANK_NAME,
                "account": settings.BANK_ACCOUNT,
                "holder": settings.BANK_HOLDER,
            }
        }
    }

