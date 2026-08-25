import asyncio
from typing import List, Optional

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter

from app.services.bot import bot

RATE_LIMIT_PER_SECOND = 25


async def send_broadcast_message(chat_id: int, text: str, image_url: Optional[str] = None) -> bool:
    try:
        if image_url:
            await bot.send_photo(chat_id=chat_id, photo=image_url, caption=text)
        else:
            await bot.send_message(chat_id=chat_id, text=text)
        return True
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        return await send_broadcast_message(chat_id, text, image_url)
    except (TelegramForbiddenError, TelegramBadRequest):
        # User blocked the bot, deleted their account, or the image URL is bad -
        # skip them and keep the broadcast going.
        return False
    except Exception as e:
        print(f"Broadcast send failed for chat {chat_id}: {e}")
        return False


async def run_mass_broadcast(telegram_ids: List[int], text: str, image_url: Optional[str] = None) -> None:
    delay = 1 / RATE_LIMIT_PER_SECOND
    sent = 0
    failed = 0

    for tg_id in telegram_ids:
        ok = await send_broadcast_message(tg_id, text, image_url)
        if ok:
            sent += 1
        else:
            failed += 1
        await asyncio.sleep(delay)

    print(f"Broadcast finished: {sent} sent, {failed} failed out of {len(telegram_ids)}")
