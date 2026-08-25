import asyncio

from aiogram import Bot

from app.core.config import settings

bot = Bot(token=settings.BOT_TOKEN)


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
