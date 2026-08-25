import hashlib
import hmac
import json
from urllib.parse import parse_qsl, unquote
from typing import Dict, Any, Optional
from fastapi import HTTPException, Security, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

security_scheme = HTTPBearer(auto_error=False)


def parse_and_verify_init_data(init_data_raw: str, bot_token: str) -> Dict[str, Any]:
    """
    Validates Telegram WebApp initData HMAC-SHA256 signature.
    Reference: Telegram WebApp documentation logic.
    """
    try:
        parsed_data = dict(parse_qsl(init_data_raw, keep_blank_values=True))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid initData format"
        )

    if "hash" not in parsed_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hash missing from initData"
        )

    hash_to_check = parsed_data.pop("hash")

    # Sort key=value pairs alphabetically joined by \n
    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(parsed_data.items(), key=lambda x: x[0])
    )

    # Secret key = HMAC_SHA256("WebAppData", bot_token)
    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode("utf-8"),
        hashlib.sha256
    ).digest()

    # Calculated hash = HMAC_SHA256(secret_key, data_check_string)
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, hash_to_check):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram initData signature"
        )

    # Deserialize user object if present
    if "user" in parsed_data:
        try:
            parsed_data["user"] = json.loads(unquote(parsed_data["user"]))
        except Exception:
            try:
                parsed_data["user"] = json.loads(parsed_data["user"])
            except Exception:
                pass

    return parsed_data


def get_current_tg_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme)
) -> Dict[str, Any]:
    """
    Dependency to extract and validate user data from 'Authorization: tma <initDataRaw>' header,
    'Authorization: Bearer <initDataRaw>' header or raw Authorization header.
    """
    init_data_raw = None

    if credentials and credentials.credentials:
        init_data_raw = credentials.credentials
    else:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            if auth_header.startswith("tma "):
                init_data_raw = auth_header[4:].strip()
            elif auth_header.startswith("Bearer "):
                init_data_raw = auth_header[7:].strip()
            else:
                init_data_raw = auth_header.strip()

    # If running in Dev/Browser mode or initData is empty/mocked
    if not init_data_raw or init_data_raw in ["null", "undefined", "dev", ""]:
        return {
            "telegram_id": 123456789,
            "username": "dev_admin",
            "first_name": "Dev",
            "last_name": "Admin",
            "is_admin": True,
            "raw_data": {}
        }

    try:
        verified_data = parse_and_verify_init_data(init_data_raw, settings.BOT_TOKEN)
    except Exception as e:
        # Fallback for local browser testing with dummy initData
        if settings.DEBUG or not settings.BOT_TOKEN:
            return {
                "telegram_id": 123456789,
                "username": "dev_admin",
                "first_name": "Dev",
                "last_name": "Admin",
                "is_admin": True,
                "raw_data": {}
            }
        raise e

    user_data = verified_data.get("user")
    if not user_data or not isinstance(user_data, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User payload missing in initData"
        )

    tg_id = user_data.get("id")
    if not tg_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram user ID missing in payload"
        )

    is_admin = int(tg_id) in settings.ADMIN_TELEGRAM_IDS or settings.DEBUG

    return {
        "telegram_id": int(tg_id),
        "username": user_data.get("username"),
        "first_name": user_data.get("first_name"),
        "last_name": user_data.get("last_name"),
        "is_admin": is_admin,
        "raw_data": verified_data
    }

