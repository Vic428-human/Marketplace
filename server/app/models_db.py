# app/models_db.py
from datetime import datetime, timezone
from typing import List

from sqlalchemy import String, Integer, Numeric, ForeignKey, DateTime, Text, Column, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    discord_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    discord_name: Mapped[str | None] = mapped_column(String(100))
    username: Mapped[str | None] = mapped_column(String(50), unique=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    provider: Mapped[str] = mapped_column(String(20), default="platform")
    level: Mapped[int] = mapped_column(Integer, default=1)
    exp: Mapped[int] = mapped_column(Integer, default=0)
    stat_attack: Mapped[int] = mapped_column(Integer, default=0)
    stat_defense: Mapped[int] = mapped_column(Integer, default=0)
    stat_agility: Mapped[int] = mapped_column(Integer, default=0)
    stat_int: Mapped[int] = mapped_column(Integer, default=0)
    stat_luk: Mapped[int] = mapped_column(Integer, default=0)
    equip_weapon_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    equip_shield_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    equip_armor_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    equip_cloak_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    equip_head_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    equip_ring_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    equip_acc1_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    equip_acc2_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="user", uselist=False)
    inventory_items: Mapped[List["InventoryItem"]] = relationship(
        "InventoryItem",
        back_populates="user",
        foreign_keys="InventoryItem.discord_id",
    )

    @property
    def uid(self) -> str:
        return self.discord_id


class ItemTemplate(Base):
    __tablename__ = "item_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    rarity: Mapped[str] = mapped_column(String(20), default="COMMON")
    slot_type: Mapped[str] = mapped_column(String(20), default="MISC")  # WEAPON/SHIELD/ARMOR/HEAD/RING/ACCESSORY/MISC
    initial_price: Mapped[float] = mapped_column(Numeric(20, 2), default=0)
    stat_attack: Mapped[int] = mapped_column(Integer, default=0)
    stat_defense: Mapped[int] = mapped_column(Integer, default=0)
    stat_agility: Mapped[int] = mapped_column(Integer, default=0)
    stat_intelligence: Mapped[int] = mapped_column(Integer, default=0)
    stat_luck: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="item_template")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 透過 Discord OAuth 的使用者辨識
    discord_id: Mapped[str] = mapped_column(String(50), nullable=False)
    discord_name: Mapped[str | None] = mapped_column(String(100))

    item_template_id: Mapped[int] = mapped_column(ForeignKey("item_templates.id"))

    side: Mapped[str] = mapped_column(String(10), nullable=False)  # 'BUY' / 'SELL'
    price: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN")
    note: Mapped[str | None] = mapped_column(Text)
    locked_amount = Column(Numeric(8, 2), default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    item_template: Mapped["ItemTemplate"] = relationship("ItemTemplate", back_populates="orders")


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String, ForeignKey("user_profiles.discord_id"), unique=True, index=True)
    balance = Column(Numeric(8, 2), default=10000)
    frozen_balance = Column(Numeric(8, 2), default=100)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user: Mapped["UserProfile"] = relationship("UserProfile", back_populates="wallet")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    discord_id: Mapped[str] = mapped_column(String(50), ForeignKey("user_profiles.discord_id"), index=True)
    item_template_id: Mapped[int] = mapped_column(ForeignKey("item_templates.id"), index=True)
    qty: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[str | None] = mapped_column(Text)
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="inventory_items",
        foreign_keys=[discord_id],
    )
    item_template: Mapped["ItemTemplate"] = relationship("ItemTemplate")


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    item_template_id: Mapped[int] = mapped_column(ForeignKey("item_templates.id"), index=True)
    price: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    taker_side: Mapped[str] = mapped_column(String(10), nullable=False)  # BUY / SELL（taker 的方向）
    maker_order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"))
    taker_order_id: Mapped[int | None] = mapped_column(ForeignKey("orders.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    item_template: Mapped["ItemTemplate"] = relationship("ItemTemplate")
