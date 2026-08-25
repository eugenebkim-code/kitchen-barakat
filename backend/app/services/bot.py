import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from app.core.config import settings

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


def _order_text(order_data: dict) -> str:
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


async def notify_owner_new_order(order_data: dict) -> None:
    """
    Sends a plain-text order summary to the owner's Telegram chat.
    Failures are logged, never raised, so a Telegram outage can't break
    order creation for the customer. Status is managed from the admin panel.
    """
    if not settings.OWNER_CHAT_ID:
        print("OWNER_CHAT_ID not configured; skipping owner notification.")
        return

    try:
        await asyncio.wait_for(
            bot.send_message(chat_id=settings.OWNER_CHAT_ID, text=_order_text(order_data)),
            timeout=15,
        )
    except Exception as e:
        print(f"Failed to notify owner about order {order_data.get('id')}: {e}")


async def start_bot_polling() -> None:
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Bot polling stopped: {e}")
