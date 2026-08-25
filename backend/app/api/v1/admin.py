from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_tg_user
from app.models.all_models import Category, MenuItem, User, Order
from app.schemas.menu import CategoryOut, CategoryWithItemsOut, MenuItemOut
from app.schemas.order import OrderOut, OrderStatusUpdate
from app.schemas.settings import ScheduleOut, ScheduleUpdate
from app.schemas.broadcast import BroadcastPayload
from app.services.storage import save_image
from app.services.schedule import compute_kitchen_status, upsert_setting
from app.services.broadcast import send_broadcast_message, run_mass_broadcast
from app.services.bot import notify_customer_status_change

router = APIRouter(prefix="/admin", tags=["Admin"])


def verify_admin(current_user: dict = Depends(get_current_tg_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


# Menu Admin Management
@router.get("/menu", response_model=List[CategoryWithItemsOut])
async def admin_get_menu(
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Full, unfiltered menu (including unavailable items) for the admin management UI.
    """
    stmt = select(Category).options(selectinload(Category.items)).order_by(Category.sort_order)
    res = await db.execute(stmt)
    return res.scalars().all()


@router.post("/menu/categories", response_model=CategoryOut)
async def create_category(
    name: str = Form(...),
    sort_order: int = Form(0),
    image: Optional[UploadFile] = File(None),
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    image_url = await save_image(image, "category") if image else None
    category = Category(name=name, sort_order=sort_order, image_url=image_url)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.patch("/menu/categories/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: int,
    name: Optional[str] = Form(None),
    sort_order: Optional[int] = Form(None),
    image: Optional[UploadFile] = File(None),
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Category).where(Category.id == category_id)
    res = await db.execute(stmt)
    category = res.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if name is not None:
        category.name = name
    if sort_order is not None:
        category.sort_order = sort_order
    if image is not None:
        category.image_url = await save_image(image, "category")

    await db.commit()
    await db.refresh(category)
    return category


@router.post("/menu/items", response_model=MenuItemOut)
async def create_menu_item(
    name: str = Form(...),
    price: int = Form(...),
    category_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    is_available: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    image_url = await save_image(image, "item") if image else None
    item = MenuItem(
        category_id=category_id,
        name=name,
        description=description,
        price=price,
        image_url=image_url,
        is_available=is_available,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/menu/items/{item_id}", response_model=MenuItemOut)
async def update_menu_item(
    item_id: int,
    name: Optional[str] = Form(None),
    price: Optional[int] = Form(None),
    category_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    is_available: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(MenuItem).where(MenuItem.id == item_id)
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if name is not None:
        item.name = name
    if price is not None:
        item.price = price
    if category_id is not None:
        item.category_id = category_id
    if description is not None:
        item.description = description
    if is_available is not None:
        item.is_available = is_available
    if image is not None:
        item.image_url = await save_image(image, "item")

    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/menu/items/{item_id}/toggle", response_model=MenuItemOut)
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
    return item


@router.delete("/menu/items/{item_id}")
async def delete_menu_item(
    item_id: int,
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(MenuItem).where(MenuItem.id == item_id)
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(item)
    await db.commit()
    return {"status": "deleted", "id": item_id}


@router.delete("/menu/categories/{category_id}")
async def delete_category(
    category_id: int,
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Deletes the category along with all of its menu items - otherwise they'd
    be orphaned (category_id set NULL) and become invisible/unmanageable
    since both the admin and customer menus are grouped by category.
    """
    stmt = select(Category).options(selectinload(Category.items)).where(Category.id == category_id)
    res = await db.execute(stmt)
    category = res.scalar_one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for item in list(category.items):
        await db.delete(item)
    await db.delete(category)
    await db.commit()
    return {"status": "deleted", "id": category_id}


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
    stmt = select(Order).options(selectinload(Order.items), selectinload(Order.user)).where(Order.id == order_id)
    res = await db.execute(stmt)
    order = res.scalar_one_or_none()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = payload.status
    telegram_id = order.user.telegram_id if order.user else None
    order_type = order.order_type
    await db.commit()
    await db.refresh(order, attribute_names=["items"])

    if telegram_id:
        await notify_customer_status_change(telegram_id, order_id, payload.status, order_type)

    return order


# Kitchen Working Hours
@router.get("/settings/schedule", response_model=ScheduleOut)
async def get_schedule(
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    return await compute_kitchen_status(db)


@router.patch("/settings/schedule", response_model=ScheduleOut)
async def update_schedule(
    payload: ScheduleUpdate,
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    if payload.open_time is not None or payload.close_time is not None:
        current = await compute_kitchen_status(db)
        await upsert_setting(db, "store_schedule", {
            "open_time": payload.open_time or current["open_time"],
            "close_time": payload.close_time or current["close_time"],
        })

    if payload.is_open_override is not None:
        await upsert_setting(db, "is_open_override", payload.is_open_override)

    await db.commit()
    return await compute_kitchen_status(db)


# Broadcast
@router.post("/broadcast")
async def broadcast_message(
    payload: BroadcastPayload,
    background_tasks: BackgroundTasks,
    admin: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    if payload.target_telegram_id:
        ok = await send_broadcast_message(payload.target_telegram_id, payload.message_text, payload.image_url)
        if not ok:
            raise HTTPException(status_code=502, detail="Failed to send test message")
        return {"status": "sent"}

    stmt = select(User.telegram_id)
    res = await db.execute(stmt)
    telegram_ids = [row[0] for row in res.all()]

    background_tasks.add_task(run_mass_broadcast, telegram_ids, payload.message_text, payload.image_url)
    return {"status": "started", "target_count": len(telegram_ids)}
