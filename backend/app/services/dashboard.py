from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.all_models import Order

KST = ZoneInfo("Asia/Seoul")

ACCEPTED_STATUSES = {"accepted", "cooking", "shipped"}
REJECTED_STATUSES = {"rejected", "cancelled"}


async def get_dashboard_stats(db: AsyncSession) -> dict:
    stmt = select(Order.created_at, Order.total_amount, Order.status)
    res = await db.execute(stmt)
    rows = res.all()

    now_kst = datetime.now(KST)
    today_start = now_kst.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())  # Monday
    month_start = today_start.replace(day=1)

    sum_today = 0
    sum_week = 0
    sum_month = 0
    count_accepted = 0
    count_rejected = 0
    count_pending = 0

    for created_at, total_amount, status in rows:
        if created_at is not None:
            # DB drivers differ on whether created_at comes back tz-aware
            # (Postgres) or naive (SQLite). Both represent a UTC instant
            # (func.now() defaults to UTC in both), so normalize the same way.
            created_at_utc = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)
            created_at_kst = created_at_utc.astimezone(KST)

            if created_at_kst >= today_start:
                sum_today += total_amount
            if created_at_kst >= week_start:
                sum_week += total_amount
            if created_at_kst >= month_start:
                sum_month += total_amount

        if status in ACCEPTED_STATUSES:
            count_accepted += 1
        elif status in REJECTED_STATUSES:
            count_rejected += 1
        elif status == "pending":
            count_pending += 1

    return {
        "sum_today": sum_today,
        "sum_week": sum_week,
        "sum_month": sum_month,
        "count_accepted": count_accepted,
        "count_rejected": count_rejected,
        "count_pending": count_pending,
    }
