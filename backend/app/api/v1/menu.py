from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.core.database import get_db
from app.models.all_models import Category, MenuItem

router = APIRouter(prefix="/menu", tags=["Menu"])


@router.get("")
async def get_menu(db: AsyncSession = Depends(get_db)):
    """
    Public menu catalog endpoint. Returns all categories with their available items.
    """
    stmt = select(Category).options(selectinload(Category.items)).order_by(Category.sort_order)
    result = await db.execute(stmt)
    categories = result.scalars().all()

    menu_response = []
    for cat in categories:
        items = [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "price": item.price,
                "image_url": item.image_url,
                "is_available": item.is_available,
                "category_id": item.category_id,
            }
            for item in cat.items if item.is_available
        ]
        menu_response.append({
            "id": cat.id,
            "name": cat.name,
            "sort_order": cat.sort_order,
            "image_url": cat.image_url,
            "items": items
        })

    return menu_response
