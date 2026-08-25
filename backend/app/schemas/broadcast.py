from typing import Optional
from pydantic import BaseModel, field_validator


class BroadcastPayload(BaseModel):
    message_text: str
    image_url: Optional[str] = None
    target_telegram_id: Optional[int] = None

    @field_validator("message_text")
    @classmethod
    def validate_message_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("message_text cannot be empty")
        return v
