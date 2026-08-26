from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class MenuItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: Optional[int] = None
    name: str
    name_ko: Optional[str] = None
    description: Optional[str] = None
    description_ko: Optional[str] = None
    price: int
    image_url: Optional[str] = None
    is_available: bool


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    name_ko: Optional[str] = None
    sort_order: int
    image_url: Optional[str] = None


class CategoryWithItemsOut(CategoryOut):
    items: List[MenuItemOut] = []
