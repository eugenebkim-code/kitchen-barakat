from datetime import datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.all_models import Setting

KST = ZoneInfo("Asia/Seoul")
DEFAULT_SCHEDULE = {"open_time": "11:00", "close_time": "23:00"}


async def get_schedule_config(db: AsyncSession) -> dict:
    stmt = select(Setting).where(Setting.key.in_(["store_schedule", "is_open_override"]))
    res = await db.execute(stmt)
    rows = {row.key: row.value for row in res.scalars().all()}

    schedule = rows.get("store_schedule") or {}
    is_open_override = rows.get("is_open_override")

    return {
        "open_time": schedule.get("open_time", DEFAULT_SCHEDULE["open_time"]),
        "close_time": schedule.get("close_time", DEFAULT_SCHEDULE["close_time"]),
        "is_open_override": True if is_open_override is None else bool(is_open_override),
    }


def is_within_schedule(open_time_str: str, close_time_str: str) -> bool:
    now = datetime.now(KST).time()
    open_t = time.fromisoformat(open_time_str)
    close_t = time.fromisoformat(close_time_str)

    if open_t <= close_t:
        return open_t <= now <= close_t
    # Overnight schedule (e.g. open 18:00, close 02:00) wraps past midnight
    return now >= open_t or now <= close_t


async def compute_kitchen_status(db: AsyncSession) -> dict:
    cfg = await get_schedule_config(db)
    is_open = cfg["is_open_override"] and is_within_schedule(cfg["open_time"], cfg["close_time"])
    return {**cfg, "is_open": is_open}


async def upsert_setting(db: AsyncSession, key: str, value) -> None:
    stmt = select(Setting).where(Setting.key == key)
    res = await db.execute(stmt)
    row = res.scalar_one_or_none()

    if row:
        row.value = value
    else:
        db.add(Setting(key=key, value=value))
