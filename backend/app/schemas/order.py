from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator

ALLOWED_ORDER_STATUSES = {"pending", "accepted", "cooking", "shipped", "rejected", "cancelled"}


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_name: str
    price: int
    quantity: int


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_type: str
    phone: str
    address: Optional[str] = None
    comment: Optional[str] = None
    items_total: int
    delivery_fee: int
    total_amount: int
    payment_screenshot_url: str
    status: str
    created_at: datetime
    items: List[OrderItemOut] = []


class OrderStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ALLOWED_ORDER_STATUSES:
            raise ValueError(f"Status must be one of {sorted(ALLOWED_ORDER_STATUSES)}")
        return v
