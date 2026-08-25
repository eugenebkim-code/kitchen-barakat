from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from typing import List

from app.core.database import get_db
from app.core.security import get_current_tg_user
from app.models.all_models import Category, MenuItem, User, Order
from app.schemas.menu import CategoryCreate, MenuItemCreate, MenuItemUpdate
from app.schemas.order import OrderOut, OrderStatusUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])


def verify_admin(current_user: dict = Depends(get_current_tg_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


# Menu Admin Management
@router.post("/menu/categories")
async def create_category(
    cat_in: CategoryCreate,
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    category = Category(name=cat_in.name, sort_order=cat_in.sort_order)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return {"id": category.id, "name": category.name, "sort_order": category.sort_order}


@router.post("/menu/items")
async def create_menu_item(
    item_in: MenuItemCreate,
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    item = MenuItem(**item_in.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"id": item.id, "name": item.name, "price": item.price, "is_available": item.is_available}


@router.patch("/menu/items/{item_id}/toggle")
async def toggle_item_availability(
    item_id: int,
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(MenuItem).where(MenuItem.id == item_id)
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.is_available = not item.is_available
    await db.commit()
    await db.refresh(item)
    return {"id": item.id, "name": item.name, "is_available": item.is_available}


# Client Analytics
@router.get("/clients")
async def get_clients_analytics(
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(User)
    res = await db.execute(stmt)
    users = res.scalars().all()

    clients_data = []
    for u in users:
        # Calculate LTV and order count
        order_stmt = select(
            func.count(Order.id).label("total_orders"),
            func.coalesce(func.sum(Order.total_amount), 0).label("ltv")
        ).where(Order.user_id == u.id)

        order_res = await db.execute(order_stmt)
        stats = order_res.one()

        clients_data.append({
            "id": u.id,
            "telegram_id": u.telegram_id,
            "username": u.username,
            "first_name": u.first_name,
            "phone": u.phone,
            "total_orders": stats.total_orders,
            "ltv": int(stats.ltv),
            "last_active": u.last_active.isoformat() if u.last_active else None
        })

    return clients_data


# Orders Management
@router.get("/orders", response_model=List[OrderOut])
async def list_orders(
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()


@router.patch("/orders/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    res = await db.execute(stmt)
    order = res.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = payload.status
    await db.commit()
    await db.refresh(order, attribute_names=["items"])
    return order
