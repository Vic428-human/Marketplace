from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from decimal import Decimal

class OrderCreate(BaseModel):
    discord_id: str
    discord_name: Optional[str] = None

    item_template_id: int
    side: str = Field(..., pattern="^(BUY|SELL)$")
    price: float = Field(..., ge=0)
    qty: int = Field(..., ge=1)
    note: Optional[str] = None


class OrderOut(BaseModel):
    id: int
    discord_id: str
    discord_name: Optional[str]
    item_template_id: int
    side: str
    price: float
    qty: int
    status: str
    note: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ItemTemplateCreate(BaseModel):
    name: str
    game: str
    rarity: str = "COMMON"


class ItemTemplateOut(BaseModel):
    id: int
    name: str
    game: str
    rarity: str

    class Config:
        from_attributes = True

class WalletTopupIn(BaseModel):
    discord_id: str
    amount: Decimal

class WalletOut(BaseModel):
    discord_id: str
    balance: Decimal
    frozen_balance: Decimal

    class Config:
        from_attributes = True

