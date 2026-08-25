import os
import json
import hmac
import hashlib
import urllib.parse
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Set test environment defaults
os.environ["BOT_TOKEN"] = "1234567890:TEST_BOT_TOKEN_FOR_PYTEST"
os.environ["ADMIN_TELEGRAM_IDS"] = "10001,10002"
os.environ["KITCHEN_WS_SECRET"] = "test_kitchen_secret"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# Async SQLite in-memory engine for fast testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


def generate_valid_tg_init_data(
    telegram_id: int = 10001,
    first_name: str = "TestUser",
    username: str = "testuser",
    bot_token: str = "1234567890:TEST_BOT_TOKEN_FOR_PYTEST"
) -> str:
    """
    Generates a cryptographically valid Telegram initData string using HMAC-SHA256.
    """
    user_data = {
        "id": telegram_id,
        "first_name": first_name,
        "username": username,
    }
    user_json = json.dumps(user_data, separators=(',', ':'))

    params = {
        "auth_date": "1700000000",
        "query_id": "AAH...",
        "user": user_json
    }

    # Sort dictionary keys alphabetically
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))

    # Calculate HMAC
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    hash_val = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

    params["hash"] = hash_val
    return urllib.parse.urlencode(params)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(async_session):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def valid_admin_init_data():
    return generate_valid_tg_init_data(telegram_id=10001, first_name="Admin", username="admin_user")


@pytest.fixture
def valid_regular_init_data():
    return generate_valid_tg_init_data(telegram_id=99999, first_name="Regular", username="regular_user")


@pytest.fixture
def admin_auth_header(valid_admin_init_data):
    return {"Authorization": f"tma {valid_admin_init_data}"}


@pytest.fixture
def user_auth_header(valid_regular_init_data):
    return {"Authorization": f"tma {valid_regular_init_data}"}
