# app/models.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CreateSellItem(BaseModel):
    userID: str = Field(..., example="Jack")
    itemType: int = Field(..., example=1) #1.收購 2.出售
    itemName: str = Field(..., example="iPhone 12 Pro Max")
    coinType: int = Field(..., example=1) #1.遊戲幣
    price: float = Field(..., ge=0,example=12999)
    itemQuantity: int = Field(...,ge=1, example=1)

class ProductDB(CreateSellItem):
    id: str
    created_at: datetime
    updated_at: datetime