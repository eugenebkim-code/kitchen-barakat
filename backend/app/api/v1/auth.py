from fastapi import APIRouter, Depends
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.security import get_current_tg_user
from app.core.config import settings
from app.models.all_models import User
from app.services.schedule import compute_kitchen_status

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
    else:
        user.username = current_tg_user.get("username")
        user.first_name = current_tg_user.get("first_name")
        user.last_name = current_tg_user.get("last_name")
        user.is_admin = current_tg_user.get("is_admin", False)
        await db.commit()

    kitchen_status = await compute_kitchen_status(db)

    return {
        "user": {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "saved_address": user.saved_address,
            "last_delivery_type": user.last_delivery_type,
            "is_admin": user.is_admin,
        },
        "settings": {
            "is_open": kitchen_status["is_open"],
            "open_time": kitchen_status["open_time"],
            "close_time": kitchen_status["close_time"],
            "delivery_fee": settings.DEFAULT_DELIVERY_FEE,
            "bank_details": {
                "bank": settings.BANK_NAME,
                "account": settings.BANK_ACCOUNT,
                "holder": settings.BANK_HOLDER,
            }
        }
    }

