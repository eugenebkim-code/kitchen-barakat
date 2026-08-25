from datetime import time
from typing import Optional
from pydantic import BaseModel, field_validator


class ScheduleOut(BaseModel):
    is_open_override: bool
    open_time: str
    close_time: str
    is_open: bool


class ScheduleUpdate(BaseModel):
    is_open_override: Optional[bool] = None
    open_time: Optional[str] = None
    close_time: Optional[str] = None

    @field_validator("open_time", "close_time")
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            time.fromisoformat(v)
        except ValueError:
            raise ValueError("Time must be in HH:MM format")
        return v
