import json
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.security import get_current_tg_user
from app.models.all_models import User, Order, OrderItem, MenuItem
from app.services.storage import save_receipt_image
from app.services.kitchen_ws import kitchen_manager
from app.services.bot import notify_owner_new_order

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("")
async def create_order(
    order_type: str = Form(...),
    phone: str = Form(...),
    address: str = Form(None),
    comment: str = Form(None),
    items: str = Form(...),  # JSON string e.g. [{"menu_item_id": 1, "quantity": 2}]
    receipt_image: UploadFile = File(...),
    current_tg_user: dict = Depends(get_current_tg_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Upsert or get user
    stmt = select(User).where(User.telegram_id == current_tg_user["telegram_id"])
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=current_tg_user["telegram_id"],
            username=current_tg_user.get("username"),
            first_name=current_tg_user.get("first_name"),
            last_name=current_tg_user.get("last_name"),
            phone=phone,
            saved_address=address,
            last_delivery_type=order_type,
            is_admin=current_tg_user.get("is_admin", False)
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.phone = phone
        if address:
            user.saved_address = address
        user.last_delivery_type = order_type

    # 2. Parse items
    try:
        items_data = json.loads(items)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON format for items")

    if not items_data or not isinstance(items_data, list):
        raise HTTPException(status_code=400, detail="Items list cannot be empty")

    # 3. Save uploaded receipt image
    image_url = await save_receipt_image(receipt_image)

    # 4. Calculate total amount
    items_total = 0
    order_items_objs = []
    ws_items = []

    for item_req in items_data:
        m_id = item_req.get("menu_item_id")
        qty = item_req.get("quantity", 1)

        stmt_m = select(MenuItem).where(MenuItem.id == m_id)
        m_res = await db.execute(stmt_m)
        menu_item = m_res.scalar_one_or_none()

        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {m_id} not found")

        item_price = menu_item.price
        items_total += item_price * qty

        order_items_objs.append({
            "menu_item_id": menu_item.id,
            "item_name": menu_item.name,
            "price": item_price,
            "quantity": qty
        })
        ws_items.append({
            "name": menu_item.name,
            "qty": qty,
            "price": item_price
        })

    delivery_fee = 3000 if order_type == "delivery" else 0
    total_amount = items_total + delivery_fee

    # 5. Save Order to Database
    new_order = Order(
        user_id=user.id,
        order_type=order_type,
        phone=phone,
        address=address,
        comment=comment,
        items_total=items_total,
        delivery_fee=delivery_fee,
        total_amount=total_amount,
        payment_screenshot_url=image_url,
        status="pending"
    )
    db.add(new_order)
    await db.commit()
    await db.refresh(new_order)

    for item_obj in order_items_objs:
        db.add(OrderItem(
            order_id=new_order.id,
            menu_item_id=item_obj["menu_item_id"],
            item_name=item_obj["item_name"],
            price=item_obj["price"],
            quantity=item_obj["quantity"]
        ))

    await db.commit()

    # 6. Broadcast NEW_ORDER event to Kitchen WebSocket clients
    ws_payload = {
        "id": new_order.id,
        "order_type": new_order.order_type,
        "created_at": new_order.created_at.isoformat() if new_order.created_at else "",
        "phone": new_order.phone,
        "address": new_order.address or "",
        "comment": new_order.comment or "",
        "items": ws_items,
        "delivery_fee": new_order.delivery_fee,
        "total_amount": new_order.total_amount,
        "screenshot_url": new_order.payment_screenshot_url
    }
    await kitchen_manager.broadcast_order(ws_payload)

    # 7. Notify owner in Telegram with a text summary
    await notify_owner_new_order(ws_payload)

    return {"order_id": new_order.id, "status": "created", "total_amount": total_amount}
