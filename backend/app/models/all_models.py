from sqlalchemy import Column, BigInteger, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(64), nullable=True)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    phone = Column(String(32), nullable=True)
    saved_address = Column(Text, nullable=True)
    last_delivery_type = Column(String(16), default="delivery")
    is_admin = Column(Boolean, default=False)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    orders = relationship("Order", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    sort_order = Column(Integer, default=0)
    image_url = Column(Text, nullable=True)

    items = relationship("MenuItem", back_populates="category")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # in KRW (₩)
    image_url = Column(Text, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("Category", back_populates="items")


class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    order_type = Column(String(16), nullable=False)  # 'delivery' | 'pickup'
    phone = Column(String(32), nullable=False)
    address = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    items_total = Column(Integer, nullable=False)
    delivery_fee = Column(Integer, default=0)
    total_amount = Column(Integer, nullable=False)
    payment_screenshot_url = Column(Text, nullable=False)
    status = Column(String(32), default="pending")  # 'pending' | 'accepted' | 'cooking' | 'shipped' | 'cancelled'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, index=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="SET NULL"), nullable=True)
    item_name = Column(String(128), nullable=False)
    price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")



class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(64), primary_key=True)
    value = Column(JSON, nullable=False)
