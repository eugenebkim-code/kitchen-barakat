import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.all_models import Order

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

STATUS_LABELS = {
    "pending": "🕓 Ожидает подтверждения",
    "accepted": "✅ Принят",
    "cooking": "🍳 Готовится",
    "shipped": "🚚 В доставке",
    "cancelled": "❌ Отменён",
}


def _order_caption(order_data: dict) -> str:
    lines = [
        f"🆕 Новый заказ #{order_data['id']}",
        f"Тип: {'Доставка' if order_data['order_type'] == 'delivery' else 'Самовывоз'}",
        f"Телефон: {order_data['phone']}",
    ]
    if order_data.get("address"):
        lines.append(f"Адрес: {order_data['address']}")
    if order_data.get("comment"):
        lines.append(f"Комментарий: {order_data['comment']}")

    lines.append("")
    for item in order_data.get("items", []):
        lines.append(f"• {item['name']} x{item['qty']} — {item['price'] * item['qty']}₩")

    lines.append("")
    if order_data.get("delivery_fee"):
        lines.append(f"Доставка: {order_data['delivery_fee']}₩")
    lines.append(f"Итого: {order_data['total_amount']}₩")

    return "\n".join(lines)


def _order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Принять", callback_data=f"order_accept:{order_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"order_reject:{order_id}"),
    ]])


async def notify_owner_new_order(order_data: dict, receipt_local_path: str) -> None:
    """
    Sends a photo message with order details and an inline Accept/Reject keyboard
    to the owner's Telegram chat. Failures are logged, never raised, so a Telegram
    outage can't break order creation for the customer.
    """
    if not settings.OWNER_CHAT_ID:
        print("OWNER_CHAT_ID not configured; skipping owner notification.")
        return

    try:
        if os.path.isfile(receipt_local_path):
            photo = FSInputFile(receipt_local_path)
            send = bot.send_photo(
                chat_id=settings.OWNER_CHAT_ID,
                photo=photo,
                caption=_order_caption(order_data),
                reply_markup=_order_keyboard(order_data["id"]),
            )
        else:
            send = bot.send_message(
                chat_id=settings.OWNER_CHAT_ID,
                text=_order_caption(order_data),
                reply_markup=_order_keyboard(order_data["id"]),
            )
        await asyncio.wait_for(send, timeout=15)
    except Exception as e:
        print(f"Failed to notify owner about order {order_data.get('id')}: {e}")


@dp.callback_query(F.data.startswith("order_accept:") | F.data.startswith("order_reject:"))
async def handle_order_action(callback: CallbackQuery):
    action, order_id_str = callback.data.split(":", 1)
    order_id = int(order_id_str)
    new_status = "accepted" if action == "order_accept" else "cancelled"

    async with AsyncSessionLocal() as session:
        order = await session.get(Order, order_id)
        if not order:
            await callback.answer("Заказ не найден", show_alert=True)
            return
        order.status = new_status
        await session.commit()

    label = STATUS_LABELS[new_status]
    base_caption = callback.message.caption or callback.message.text or ""
    try:
        new_text = f"{base_caption}\n\nСтатус: {label}"
        if callback.message.caption is not None:
            await callback.message.edit_caption(caption=new_text, reply_markup=None)
        else:
            await callback.message.edit_text(text=new_text, reply_markup=None)
    except TelegramAPIError:
        pass

    await callback.answer(f"Заказ #{order_id}: {label}")


async def start_bot_polling() -> None:
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Bot polling stopped: {e}")
