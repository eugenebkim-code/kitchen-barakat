import asyncio
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import engine, Base, ensure_schema_migrations
from app.core.seed import seed_db
from app.api.v1 import api_router
from app.api.v1 import ws
from app.services.bot import bot, start_bot_polling

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
# Mounted at the bare root (not under /api/v1) per SPEC.md: WS /ws/kitchen
app.include_router(ws.router)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await ensure_schema_migrations()
    await seed_db()
    asyncio.create_task(start_bot_polling())


@app.on_event("shutdown")
async def shutdown_event():
    await bot.session.close()


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok", "project": settings.PROJECT_NAME}

