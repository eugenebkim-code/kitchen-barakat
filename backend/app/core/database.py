from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def ensure_schema_migrations():
    """
    Minimal in-place migration for columns added after the initial deploy
    (there's no Alembic in this project). Base.metadata.create_all only
    creates missing tables, so columns added to existing tables need this.
    """
    async with engine.begin() as conn:
        if conn.dialect.name == "postgresql":
            await conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS image_url TEXT"))
            await conn.execute(text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS name_ko VARCHAR(64)"))
            await conn.execute(text("ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS name_ko VARCHAR(128)"))
            await conn.execute(text("ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS description_ko TEXT"))
        else:
            for stmt in (
                "ALTER TABLE categories ADD COLUMN image_url TEXT",
                "ALTER TABLE categories ADD COLUMN name_ko VARCHAR(64)",
                "ALTER TABLE menu_items ADD COLUMN name_ko VARCHAR(128)",
                "ALTER TABLE menu_items ADD COLUMN description_ko TEXT",
            ):
                try:
                    await conn.execute(text(stmt))
                except Exception:
                    pass
