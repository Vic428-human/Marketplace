from datetime import datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field, EmailStr


class AuthRegisterIn(BaseModel):
    provider: str = Field("platform", pattern="^(platform|discord)$")
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    password: Optional[str] = Field(None, min_length=6, max_length=128)
    discord_id: Optional[str] = Field(None, min_length=1)


class AuthLoginIn(BaseModel):
    provider: str = Field("platform", pattern="^(platform|discord)$")
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=1)
    discord_id: Optional[str] = Field(None, min_length=1)


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


class OrderBookEntry(BaseModel):
    price: float
    qty: int


class ItemTemplateCreate(BaseModel):
    name: str
    rarity: str = "COMMON"
    slot_type: str = Field("MISC", description="WEAPON/SHIELD/ARMOR/HEAD/RING/ACCESSORY/MISC")
    initial_price: Decimal = Field(0, example="100.00")
    stat_attack: int = 0
    stat_defense: int = 0
    stat_agility: int = 0
    stat_intelligence: int = 0
    stat_luck: int = 0


class ItemTemplateOut(BaseModel):
    id: int
    name: str
    rarity: str
    slot_type: str
    initial_price: Decimal = Field(0, example="100.00")
    stat_attack: int
    stat_defense: int
    stat_agility: int
    stat_intelligence: int
    stat_luck: int

    class Config:
        from_attributes = True


class WalletTopupIn(BaseModel):
    discord_id: str
    amount: Decimal = Field(..., example="10000.00")


class WalletOut(BaseModel):
    discord_id: str
    balance: Decimal = Field(..., example="10000.00")
    frozen_balance: Decimal = Field(..., example="100.00")

    class Config:
        from_attributes = True


class UserProfileUpsertIn(BaseModel):
    discord_id: str
    discord_name: Optional[str] = None


class UserProfileOut(BaseModel):
    discord_id: str
    discord_name: Optional[str] = None
    uid: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    level: int
    exp: int
    next_exp_needed: int | None = None
    provider: Optional[str] = None
    stat_points: int = 0
    stat_attack: int =0
    stat_defense: int = 0
    stat_agility: int = 0
    stat_int: int = 0
    stat_luk: int = 0
    equip_weapon_id: Optional[int] = None
    equip_shield_id: Optional[int] = None
    equip_armor_id: Optional[int] = None
    equip_cloak_id: Optional[int] = None
    equip_head_id: Optional[int] = None
    equip_ring_id: Optional[int] = None
    equip_acc1_id: Optional[int] = None
    equip_acc2_id: Optional[int] = None

    class Config:
        from_attributes = True


class AddExpIn(BaseModel):
    discord_id: str
    delta: int = Field(..., ge=1, example=50)


class StatAllocateIn(BaseModel):
    attack: int = Field(0, ge=0)
    defense: int = Field(0, ge=0)
    agility: int = Field(0, ge=0)
    intelligence: int = Field(0, ge=0)
    luck: int = Field(0, ge=0)

class InventoryGrantIn(BaseModel):
    discord_id: str
    item_template_id: int
    qty: int = Field(..., ge=1, example=1)
    note: Optional[str] = None


class UserEquipmentUpdate(BaseModel):
    weapon_id: Optional[int] = None
    weapon_template_id: Optional[int] = None
    shield_id: Optional[int] = None
    shield_template_id: Optional[int] = None
    armor_id: Optional[int] = None
    armor_template_id: Optional[int] = None
    cloak_id: Optional[int] = None
    cloak_template_id: Optional[int] = None
    head_id: Optional[int] = None
    head_template_id: Optional[int] = None
    ring_id: Optional[int] = None
    ring_template_id: Optional[int] = None
    acc1_id: Optional[int] = None
    acc1_template_id: Optional[int] = None
    acc2_id: Optional[int] = None
    acc2_template_id: Optional[int] = None


class InventoryItemOut(BaseModel):
    id: int
    discord_id: str
    item_template_id: int
    qty: int
    note: Optional[str]
    acquired_at: datetime
    item_template: Optional[ItemTemplateOut] = None

    class Config:
        from_attributes = True


class InventorySummaryOut(BaseModel):
    discord_id: str
    total_qty: int
    capacity: int
    items: List[InventoryItemOut]

    class Config:
        from_attributes = True


class TradeOut(BaseModel):
    id: int
    item_template_id: int
    price: float
    qty: int
    taker_side: str
    created_at: datetime

    class Config:
        from_attributes = True


class SkillCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class SkillCategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileOut


class MonsterCreate(BaseModel):
    name: str
    level: int = Field(..., ge=1)
    area: str
    drop_items: List[str] = Field(default_factory=list, description="掉落物品清單")
    attack: int = Field(..., ge=0)
    hp: int = Field(..., ge=0)
    defense: int = Field(..., ge=0)
    skill_category_ids: List[int] = Field(default_factory=list, description="技能類別 ID 清單，可為空")
    icon: Optional[str] = Field(None, description="怪物圖示 (emoji 或圖片 URL)")
    icon: str = Field(... , description="怪物圖示")

class MonsterOut(BaseModel):
    id: int
    name: str
    level: int
    area: str
    drop_items: List[str]
    attack: int
    hp: int
    defense: int
    created_at: datetime
    skill_categories: List[SkillCategoryOut] = []
    drops: List["MonsterDropOut"] = []
    icon: Optional[str] = None

    class Config:
        from_attributes = True


class MonsterDropCreate(BaseModel):
    item_template_id: int
    drop_rate: float = Field(..., ge=0, le=1, description="0~1 之間")
    qty_min: int = Field(1, ge=1)
    qty_max: int = Field(1, ge=1)


class MonsterDropOut(BaseModel):
    monster_id: int
    item_template_id: int
    drop_rate: float
    qty_min: int
    qty_max: int
    item_template: Optional[ItemTemplateOut] = None

    class Config:
        from_attributes = True


class DungeonCreate(BaseModel):
    name: str
    level_req: int = Field(..., ge=1)
    difficulty: str
    icon: Optional[str] = None
    boss_id: Optional[int] = Field(None, description="對應怪物 ID")


class DungeonOut(BaseModel):
    id: int
    name: str
    level_req: int
    difficulty: str
    icon: Optional[str] = None
    boss_id: Optional[int] = None
    created_at: datetime
    boss: Optional[MonsterOut] = None
    monsters: List[MonsterOut] = []

    class Config:
        from_attributes = True


class DungeonMonsterAttach(BaseModel):
    monster_id: int


# Resolve forward refs
MonsterOut.update_forward_refs()
