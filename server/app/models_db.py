# app/models_db.py
from datetime import datetime, timezone
from typing import List

from sqlalchemy import String, Integer, Numeric, ForeignKey, DateTime, Text,Column,func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class ItemTemplate(Base):
    __tablename__ = "item_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    game: Mapped[str] = mapped_column(String(50), nullable=False)
    rarity: Mapped[str] = mapped_column(String(20), default="COMMON")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="item_template")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # 由 Discord OAuth 取得的使用者識別資訊
    discord_id: Mapped[str] = mapped_column(String(50), nullable=False)
    discord_name: Mapped[str | None] = mapped_column(String(100))

    item_template_id: Mapped[int] = mapped_column(ForeignKey("item_templates.id"))

    side: Mapped[str] = mapped_column(String(10), nullable=False)  # 'BUY' / 'SELL'
    price: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN")
    note: Mapped[str | None] = mapped_column(Text)
    locked_amount = Column(Numeric(8, 2), default=0)  # 為這筆單凍結多少保證金

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
    discord_id = Column(String, unique=True, index=True)
    balance = Column(Numeric(8, 2), default=10000)          # 總餘額
    frozen_balance = Column(Numeric(8, 2), default=100)   # 已凍結
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())