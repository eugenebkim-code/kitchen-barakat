from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class MenuItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: int
    image_url: Optional[str] = None
    is_available: bool


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sort_order: int
    image_url: Optional[str] = None


class CategoryWithItemsOut(CategoryOut):
    items: List[MenuItemOut] = []
