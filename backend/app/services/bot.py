import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.all_models import Order

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

WELCOME_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "welcome.jpg")
WELCOME_TEXT = (
    'Добро пожаловать в Кафе "БАРАКАТ"! 🍽️\n\n'
    "Традиционная узбекская кухня в городе Дунпо, Корея.\n"
    "Нажмите кнопку ниже, чтобы открыть меню и сделать заказ."
)


def _webapp_keyboard() -> InlineKeyboardMarkup | None:
    if not settings.FRONTEND_URL:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🍽️ Открыть меню", web_app=WebAppInfo(url=settings.FRONTEND_URL))
    ]])


@dp.message(CommandStart())
async def handle_start(message: Message) -> None:
    keyboard = _webapp_keyboard()

    try:
        photo = FSInputFile(WELCOME_IMAGE_PATH)
        await message.answer_photo(photo=photo, caption=WELCOME_TEXT, reply_markup=keyboard)
    except Exception as e:
        print(f"Failed to send welcome photo, falling back to text: {e}")
        await message.answer(WELCOME_TEXT, reply_markup=keyboard)


# --- Owner order notification -------------------------------------------------

ORDER_STATUS_LABELS_RU = {
    "accepted": "✅ Принято",
    "cooking": "🍳 Готовится",
    "shipped": "🚚 Отправлен",
    "rejected": "❌ Отклонён",
}


def _owner_order_caption(order_data: dict) -> str:
    if order_data["order_type"] == "delivery":
        method_line = f"Способ: ДОСТАВКА (+{order_data.get('delivery_fee', 0):,} ₩) | Тел: {order_data['phone']}"
    else:
        method_line = f"Способ: САМОВЫВОЗ | Тел: {order_data['phone']}"

    lines = [f"НОВЫЙ ЗАКАЗ #{order_data['id']}", method_line]

    if order_data.get("address"):
        lines.append(f"Адрес: {order_data['address']}")
    if order_data.get("comment"):
        lines.append(f"Комментарий: {order_data['comment']}")

    items_str = "; ".join(
        f"{item['name']} ({item['qty']} шт.) — {item['price'] * item['qty']:,} ₩"
        for item in order_data.get("items", [])
    )
    lines.append(f"Состав: {items_str}")
    lines.append(f"ИТОГО К ОПЛАТЕ: {order_data['total_amount']:,} ₩")
    lines.append("[Прикреплен скриншот банковского перевода]")

    return "\n".join(lines)


def _owner_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"order_status:{order_id}:accepted"),
            InlineKeyboardButton(text="🍳 Готовится", callback_data=f"order_status:{order_id}:cooking"),
        ],
        [
            InlineKeyboardButton(text="🚚 Отправлен", callback_data=f"order_status:{order_id}:shipped"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"order_status:{order_id}:rejected"),
        ],
    ])


async def notify_owner_new_order(order_data: dict, receipt_local_path: str) -> None:
    """
    Sends the receipt photo with order details and status-control buttons to
    the owner's Telegram chat. Failures are logged, never raised, so a
    Telegram outage can't break order creation for the customer.
    """
    if not settings.OWNER_CHAT_ID:
        print("OWNER_CHAT_ID not configured; skipping owner notification.")
        return

    caption = _owner_order_caption(order_data)
    keyboard = _owner_order_keyboard(order_data["id"])

    try:
        if os.path.isfile(receipt_local_path):
            photo = FSInputFile(receipt_local_path)
            send = bot.send_photo(
                chat_id=settings.OWNER_CHAT_ID,
                photo=photo,
                caption=caption,
                reply_markup=keyboard,
            )
        else:
            send = bot.send_message(chat_id=settings.OWNER_CHAT_ID, text=caption, reply_markup=keyboard)
        await asyncio.wait_for(send, timeout=15)
    except Exception as e:
        print(f"Failed to notify owner about order {order_data.get('id')}: {e}")


# --- Customer status notification ---------------------------------------------

def _customer_status_message(order_id: int, status: str, order_type: str) -> str:
    if status == "shipped":
        if order_type == "pickup":
            return f"✅ Ваш заказ #{order_id} готов! Ждём вас для самовывоза."
        return f"🚚 Ваш заказ #{order_id} передан в доставку!"

    messages = {
        "accepted": f"✅ Ваш заказ #{order_id} принят и передан на кухню!",
        "cooking": f"🍳 Ваш заказ #{order_id} готовится!",
        "rejected": f"❌ К сожалению, ваш заказ #{order_id} отклонён. Свяжитесь с нами для уточнения деталей.",
        "cancelled": f"❌ Ваш заказ #{order_id} отменён.",
    }
    return messages.get(status, f"Статус вашего заказа #{order_id} изменён: {status}")


async def notify_customer_status_change(telegram_id: int, order_id: int, status: str, order_type: str) -> None:
    if not telegram_id:
        return

    try:
        await asyncio.wait_for(
            bot.send_message(chat_id=telegram_id, text=_customer_status_message(order_id, status, order_type)),
            timeout=15,
        )
    except Exception as e:
        print(f"Failed to notify customer {telegram_id} about order {order_id} status change: {e}")


@dp.callback_query(F.data.startswith("order_status:"))
async def handle_order_status_callback(callback: CallbackQuery) -> None:
    try:
        _, order_id_str, new_status = callback.data.split(":", 2)
        order_id = int(order_id_str)
    except ValueError:
        await callback.answer("Некорректные данные", show_alert=True)
        return

    async with AsyncSessionLocal() as session:
        stmt = select(Order).options(selectinload(Order.user)).where(Order.id == order_id)
        result = await session.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            await callback.answer("Заказ не найден", show_alert=True)
            return

        order.status = new_status
        await session.commit()

        telegram_id = order.user.telegram_id if order.user else None
        order_type = order.order_type

    label = ORDER_STATUS_LABELS_RU.get(new_status, new_status)

    try:
        base_caption = (callback.message.caption or "").split("\n\nСтатус:")[0]
        await callback.message.edit_caption(
            caption=f"{base_caption}\n\nСтатус: {label}",
            reply_markup=callback.message.reply_markup,
        )
    except TelegramBadRequest:
        pass

    await callback.answer(f"Заказ #{order_id}: {label}")

    if telegram_id:
        await notify_customer_status_change(telegram_id, order_id, new_status, order_type)


async def start_bot_polling() -> None:
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Bot polling stopped: {e}")
