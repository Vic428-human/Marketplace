# app/main.py
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import List
import json

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
import hashlib

def api_error(code: int, message: str, status_code: int = 400):
    raise HTTPException(status_code=status_code, detail={"code": code, "message": message})

from . import models_db
from .db import Base, engine, get_db
from .schemas import (
    AddExpIn,
    AuthRegisterIn,
    AuthLoginIn,
    InventoryGrantIn,
    InventoryItemOut,
    InventorySummaryOut,
    ItemTemplateCreate,
    ItemTemplateOut,
    OrderCreate,
    OrderOut,
    OrderBookEntry,
    TradeOut,
    UserProfileOut,
    UserProfileUpsertIn,
    UserEquipmentUpdate,
    WalletOut,
    WalletTopupIn,
    SkillCategoryCreate,
    SkillCategoryOut,
    MonsterCreate,
    MonsterOut,
    DungeonCreate,
    DungeonOut,
)


def serialize_monster(monster: models_db.Monster) -> MonsterOut:
    try:
        drop_items = json.loads(monster.drop_items or "[]")
    except Exception:
        drop_items = []

    return MonsterOut(
        id=monster.id,
        name=monster.name,
        level=monster.level,
        area=monster.area,
        drop_items=drop_items,
        attack=monster.attack,
        hp=monster.hp,
        defense=monster.defense,
        created_at=monster.created_at,
        skill_categories=monster.skill_categories or [],
    )


def serialize_dungeon(dungeon: models_db.Dungeon) -> DungeonOut:
    return DungeonOut(
        id=dungeon.id,
        name=dungeon.name,
        level_req=dungeon.level_req,
        difficulty=dungeon.difficulty,
        icon=dungeon.icon,
        boss_id=dungeon.boss_id,
        created_at=dungeon.created_at,
        boss=serialize_monster(dungeon.boss) if dungeon.boss else None,
    )

LEVEL_UP_EXP = 100
BAG_CAPACITY = 500


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Virtual Item Exchange", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 一律放行，含 file:// (null origin)
    allow_origin_regex=".*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)


def ensure_user(
    db: Session,
    discord_id: str,
    discord_name: str | None = None,
    provider: str | None = None,
    email: str | None = None,
    username: str | None = None,
    password_hash: str | None = None,
) -> models_db.UserProfile:
    user = db.get(models_db.UserProfile, discord_id)
    if not user:
        user = models_db.UserProfile(
            discord_id=discord_id,
            discord_name=discord_name,
            provider=provider or "platform",
            email=email,
            username=username,
            password_hash=password_hash,
            level=1,
            exp=0,
            stat_attack=0,
            stat_defense=0,
            stat_agility=0,
            stat_int=0,
            stat_luk=0,
        )
        db.add(user)
        db.flush()
    else:
        if discord_name and user.discord_name != discord_name:
            user.discord_name = discord_name
        if provider and user.provider != provider:
            user.provider = provider
        if email and user.email != email:
            user.email = email
        if username and user.username != username:
            user.username = username
        if password_hash:
            user.password_hash = password_hash
    return user


def ensure_wallet(db: Session, discord_id: str) -> models_db.Wallet:
    wallet = (
        db.query(models_db.Wallet)
        .filter(models_db.Wallet.discord_id == discord_id)
        .with_for_update()
        .first()
    )
    if not wallet:
        wallet = models_db.Wallet(discord_id=discord_id, balance=0, frozen_balance=0)
        db.add(wallet)
        db.flush()
    return wallet


def apply_exp(user: models_db.UserProfile, delta: int) -> None:
    user.exp += delta
    while user.exp >= LEVEL_UP_EXP:
        user.exp -= LEVEL_UP_EXP
        user.level += 1


def get_inventory_row(db: Session, discord_id: str, item_template_id: int) -> models_db.InventoryItem | None:
    return (
        db.query(models_db.InventoryItem)
        .filter(
            models_db.InventoryItem.discord_id == discord_id,
            models_db.InventoryItem.item_template_id == item_template_id,
        )
        .with_for_update()
        .first()
    )


def get_inventory_total_qty(db: Session, discord_id: str) -> int:
    total = (
        db.query(func.coalesce(func.sum(models_db.InventoryItem.qty), 0))
        .filter(models_db.InventoryItem.discord_id == discord_id)
        .scalar()
    )
    return int(total or 0)


def match_order(db: Session, order: models_db.Order) -> None:
    """
    價格優先、時間優先，僅在「同價」時成交。
    """
    remaining_qty = order.qty
    opposite_side = "SELL" if order.side == "BUY" else "BUY"

    while remaining_qty > 0:
        opp_q = (
            db.query(models_db.Order)
            .filter(
                models_db.Order.status == "OPEN",
                models_db.Order.item_template_id == order.item_template_id,
                models_db.Order.side == opposite_side,
                models_db.Order.price == order.price,  # 同價才成交
            )
            .order_by(models_db.Order.created_at.asc())
        )

        target = opp_q.with_for_update().first()
        if not target:
            break

        trade_qty = min(remaining_qty, target.qty)
        trade_price = Decimal(target.price)
        trade_value = trade_price * Decimal(trade_qty)

        buyer_order = order if order.side == "BUY" else target
        seller_order = target if order.side == "BUY" else order

        buyer_wallet = ensure_wallet(db, buyer_order.discord_id)
        seller_wallet = ensure_wallet(db, seller_order.discord_id)

        buyer_wallet.frozen_balance = buyer_wallet.frozen_balance - trade_value
        if buyer_wallet.frozen_balance < 0:
            buyer_wallet.frozen_balance = 0
        seller_wallet.balance = seller_wallet.balance + trade_value

        seller_total_before = seller_order.qty
        seller_order.qty = seller_order.qty - trade_qty
        seller_consumed_ratio = (
            Decimal(trade_qty) / Decimal(seller_total_before) if seller_total_before else Decimal("1")
        )
        release_deposit = (Decimal(seller_order.locked_amount or 0) * seller_consumed_ratio).quantize(
            Decimal("0.01")
        )
        seller_wallet.frozen_balance = seller_wallet.frozen_balance - release_deposit
        if seller_wallet.frozen_balance < 0:
            seller_wallet.frozen_balance = 0
        seller_order.locked_amount = Decimal(seller_order.locked_amount or 0) - release_deposit
        if seller_order.locked_amount < 0:
            seller_order.locked_amount = Decimal("0")

        inv = get_inventory_row(db, buyer_order.discord_id, order.item_template_id)
        if not inv:
            inv = models_db.InventoryItem(
                discord_id=buyer_order.discord_id,
                item_template_id=order.item_template_id,
                qty=0,
                note="成交獲得",
            )
            db.add(inv)
        inv.qty = inv.qty + trade_qty

        trade = models_db.Trade(
            item_template_id=order.item_template_id,
            price=trade_price,
            qty=trade_qty,
            taker_side=order.side,
            maker_order_id=target.id,
            taker_order_id=order.id,
        )
        db.add(trade)

        if target.qty <= trade_qty:
            target.status = "FILLED"
            target.locked_amount = Decimal("0")
            target.qty = 0
        else:
            target.status = "PARTIAL"
            target.qty = target.qty - trade_qty

        remaining_qty -= trade_qty
        if remaining_qty <= 0:
            order.status = "FILLED"
            if order.side == "BUY":
                buyer_wallet.frozen_balance = buyer_wallet.frozen_balance - Decimal(order.locked_amount or 0)
                if buyer_wallet.frozen_balance < 0:
                    buyer_wallet.frozen_balance = 0
            else:
                seller_wallet.frozen_balance = seller_wallet.frozen_balance - Decimal(order.locked_amount or 0)
                if seller_wallet.frozen_balance < 0:
                    seller_wallet.frozen_balance = 0
            order.locked_amount = Decimal("0")
            order.qty = 0
        else:
            order.status = "PARTIAL"
            order.qty = remaining_qty
            if order.side == "BUY":
                order.locked_amount = Decimal(order.locked_amount or 0) - trade_value
            else:
                order.locked_amount = Decimal(order.locked_amount or 0) - release_deposit
                if order.locked_amount < 0:
                    order.locked_amount = Decimal("0")


# 建立道具模板
@app.post("/api/item-templates", response_model=ItemTemplateOut, tags=["Item"])
def create_item_template(payload: ItemTemplateCreate, db: Session = Depends(get_db)):
    item = models_db.ItemTemplate(
        name=payload.name,
        rarity=payload.rarity,
        slot_type=(payload.slot_type or "MISC").upper(),
        initial_price=payload.initial_price,
        stat_attack=payload.stat_attack,
        stat_defense=payload.stat_defense,
        stat_agility=payload.stat_agility,
        stat_intelligence=payload.stat_intelligence,
        stat_luck=payload.stat_luck,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/api/item-templates", response_model=List[ItemTemplateOut], tags=["Item"])
def list_item_templates(db: Session = Depends(get_db)):
    items = db.query(models_db.ItemTemplate).order_by(models_db.ItemTemplate.id).all()
    return items


# 建立訂單
@app.post("/api/orders", response_model=OrderOut, tags=["Order"])
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    item = db.query(models_db.ItemTemplate).get(payload.item_template_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item template not found")

    required_amount = Decimal(payload.price) * Decimal(payload.qty)

    try:
        user = ensure_user(db, payload.discord_id, payload.discord_name)
        wallet = ensure_wallet(db, payload.discord_id)

        available = wallet.balance - wallet.frozen_balance

        if payload.side == "BUY":
            if available < required_amount:
                raise HTTPException(status_code=400, detail="餘額不足，無法下買單")
            wallet.frozen_balance = wallet.frozen_balance + required_amount
            locked_amount = required_amount

        elif payload.side == "SELL":
            deposit = required_amount * Decimal("0.1")
            if available < deposit:
                raise HTTPException(status_code=400, detail="餘額不足，無法掛賣單（保證金不足）")

            inv_row = get_inventory_row(db, user.discord_id, payload.item_template_id)
            if not inv_row or inv_row.qty < payload.qty:
                raise HTTPException(status_code=400, detail="背包數量不足，無法掛賣單")

            wallet.frozen_balance = wallet.frozen_balance + deposit
            inv_row.qty = inv_row.qty - payload.qty
            locked_amount = deposit
        else:
            raise HTTPException(status_code=400, detail="side 必須是 BUY 或 SELL")

        order = models_db.Order(
            discord_id=user.discord_id,
            discord_name=payload.discord_name,
            item_template_id=payload.item_template_id,
            side=payload.side,
            price=payload.price,
            qty=payload.qty,
            status="OPEN",
            note=payload.note,
            locked_amount=locked_amount,
        )

        db.add(order)
        db.flush()

        # 僅在有同價對手單時撮合，否則保留掛單
        opp_side = "SELL" if order.side == "BUY" else "BUY"
        opp_exists = (
            db.query(models_db.Order)
            .filter(
                models_db.Order.status == "OPEN",
                models_db.Order.item_template_id == order.item_template_id,
                models_db.Order.side == opp_side,
                models_db.Order.price == order.price,
            )
            .first()
            is not None
        )
        if opp_exists:
            match_order(db, order)

        db.commit()
        db.refresh(order)
        return order

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise


@app.get("/api/orderbook/{item_template_id}", response_model=List[OrderBookEntry], tags=["Order"])
def get_orderbook(item_template_id: int, side: str | None = None, db: Session = Depends(get_db)):
    item = db.query(models_db.ItemTemplate).get(item_template_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item template not found")

    query = (
        db.query(models_db.Order.price, func.sum(models_db.Order.qty).label("qty"))
        .filter(
        models_db.Order.item_template_id == item_template_id,
        models_db.Order.status == "OPEN",
        )
        .group_by(models_db.Order.price)
    )

    if side in ("BUY", "SELL"):
        query = query.filter(models_db.Order.side == side)

    # 賣單：價高到低；買單：價低到高
    if side == "SELL":
        query = query.order_by(models_db.Order.price.desc())
    elif side == "BUY":
        query = query.order_by(models_db.Order.price.asc())
    else:
        query = query.order_by(models_db.Order.price.desc())

    rows = query.all()
    return [OrderBookEntry(price=float(r.price), qty=int(r.qty)) for r in rows]


@app.get("/api/orders/by-user/{discord_id}", response_model=List[OrderOut], tags=["Order"])
def get_orders_by_user(discord_id: str, db: Session = Depends(get_db)):
    orders = (
        db.query(models_db.Order)
        .filter(models_db.Order.discord_id == discord_id)
        .order_by(models_db.Order.created_at.desc())
        .all()
    )
    return orders


@app.post("/api/orders/{order_id}/cancel", response_model=OrderOut, tags=["Order"])
def cancel_order(order_id: int, discord_id: str, db: Session = Depends(get_db)):
    order = db.query(models_db.Order).with_for_update().get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.discord_id != discord_id:
        raise HTTPException(status_code=403, detail="只能取消自己的訂單")
    if order.status != "OPEN":
        raise HTTPException(status_code=400, detail="訂單已成交或已取消")

    wallet = ensure_wallet(db, discord_id)

    if order.side == "BUY":
        wallet.frozen_balance = wallet.frozen_balance - Decimal(order.locked_amount or 0)
        if wallet.frozen_balance < 0:
            wallet.frozen_balance = 0
    else:
        wallet.frozen_balance = wallet.frozen_balance - Decimal(order.locked_amount or 0)
        if wallet.frozen_balance < 0:
            wallet.frozen_balance = 0

        inv_row = get_inventory_row(db, discord_id, order.item_template_id)
        if not inv_row:
            inv_row = models_db.InventoryItem(
                discord_id=discord_id,
                item_template_id=order.item_template_id,
                qty=0,
                note="取消訂單退回",
            )
            db.add(inv_row)
        inv_row.qty = inv_row.qty + order.qty

    order.status = "CANCELLED"
    order.locked_amount = Decimal("0")
    db.commit()
    db.refresh(order)
    return order


@app.get("/api/trades/{item_template_id}", response_model=List[TradeOut], tags=["Market"])
def list_trades(
    item_template_id: int,
    limit: int = 200,
    db: Session = Depends(get_db),
):
    limit = min(max(limit, 1), 500)
    trades = (
        db.query(models_db.Trade)
        .filter(models_db.Trade.item_template_id == item_template_id)
        .order_by(models_db.Trade.created_at.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(trades))


def hash_password(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def verify_password(raw: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    return hash_password(raw) == hashed


def user_to_out(user: models_db.UserProfile) -> UserProfileOut:
    return UserProfileOut(
        discord_id=user.discord_id,
        uid=user.discord_id,
        discord_name=user.discord_name,
        username=user.username,
        email=user.email,
        level=user.level,
        exp=user.exp,
        provider=user.provider,
        stat_attack=user.stat_attack,
        stat_defense=user.stat_defense,
        stat_agility=user.stat_agility,
        stat_int=user.stat_int,
        stat_luk=user.stat_luk,
        equip_weapon_id=user.equip_weapon_id,
        equip_shield_id=user.equip_shield_id,
        equip_armor_id=user.equip_armor_id,
        equip_cloak_id=user.equip_cloak_id,
        equip_head_id=user.equip_head_id,
        equip_ring_id=user.equip_ring_id,
        equip_acc1_id=user.equip_acc1_id,
        equip_acc2_id=user.equip_acc2_id,
    )


def generate_uid(db: Session) -> str:
    last = (
        db.query(models_db.UserProfile)
        .filter(models_db.UserProfile.discord_id.like("A%"))
        .order_by(models_db.UserProfile.discord_id.desc())
        .first()
    )
    if not last or not last.discord_id[1:].isdigit():
        return "A000001"
    num = int(last.discord_id[1:]) + 1
    return f"A{num:06d}"


@app.post("/api/auth/register", response_model=UserProfileOut, tags=["Auth"])
def register_user(payload: AuthRegisterIn, db: Session = Depends(get_db)):
    provider = (payload.provider or "platform").lower()
    if provider not in ("platform", "discord"):
        api_error(2008, "provider 不正確", status_code=400)

    username = (payload.username or "").strip() if payload.username else None
    email = (payload.email or "").strip().lower() if payload.email else None
    password = payload.password or ""

    if provider == "platform":
        if not email:
            api_error(2009, "Email 必填", status_code=400)
        if not username:
            api_error(2010, "用戶名稱必填", status_code=400)
        if len(password) < 6:
            api_error(2001, "密碼至少 6 碼")
        # 唯一性檢查
        if db.query(models_db.UserProfile).filter(models_db.UserProfile.email == email).first():
            api_error(2002, "Email 已被註冊")
        if db.query(models_db.UserProfile).filter(models_db.UserProfile.username == username).first():
            api_error(2003, "用戶名稱已被使用")
        uid = generate_uid(db)
        pwd_hash = hash_password(password)
        user = ensure_user(
            db,
            uid,
            username,
            provider="platform",
            email=email,
            username=username,
            password_hash=pwd_hash,
        )
    else:
        # provider == discord
        discord_id = (payload.discord_id or "").strip()
        if not discord_id:
            api_error(2011, "缺少 Discord ID", status_code=400)
        # 如果已存在，直接回傳（視為登入）
        existing = db.get(models_db.UserProfile, discord_id)
        if existing:
            return user_to_out(existing)
        # 允許 email/username 缺省，補上預設
        if email and db.query(models_db.UserProfile).filter(models_db.UserProfile.email == email).first():
            api_error(2002, "Email 已被註冊")
        if username and db.query(models_db.UserProfile).filter(models_db.UserProfile.username == username).first():
            api_error(2003, "用戶名稱已被使用")
        if not email:
            email = f"{discord_id}@example.com"
        if not username:
            username = discord_id
        if password and len(password) < 6:
            api_error(2001, "密碼至少 6 碼")
        pwd_hash = hash_password(password or f"discord-{discord_id}")
        user = ensure_user(
            db,
            discord_id,
            username,
            provider="discord",
            email=email,
            username=username,
            password_hash=pwd_hash,
        )

    ensure_wallet(db, user.discord_id)
    db.commit()
    db.refresh(user)
    return user_to_out(user)


@app.post("/api/auth/login", response_model=UserProfileOut, tags=["Auth"])
def login_user(payload: AuthLoginIn, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    password = payload.password

    user = db.query(models_db.UserProfile).filter(models_db.UserProfile.email == email).first()
    if not user:
        api_error(2005, "帳號未註冊", status_code=404)
    if not verify_password(password, user.password_hash):
        api_error(2004, "帳號或密碼錯誤", status_code=401)

    return user_to_out(user)


@app.post("/api/users/upsert", response_model=UserProfileOut, tags=["User"])
def upsert_user(payload: UserProfileUpsertIn, db: Session = Depends(get_db)):
    user = ensure_user(db, payload.discord_id, payload.discord_name, provider="discord")
    db.commit()
    db.refresh(user)
    return user_to_out(user)


@app.get("/api/users/{discord_id}", response_model=UserProfileOut, tags=["User"])
def get_user(discord_id: str, db: Session = Depends(get_db)):
    user = db.get(models_db.UserProfile, discord_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_out(user)


@app.post("/api/users/add-exp", response_model=UserProfileOut, tags=["User"])
def add_exp(payload: AddExpIn, db: Session = Depends(get_db)):
    user = ensure_user(db, payload.discord_id)
    apply_exp(user, payload.delta)
    db.commit()
    db.refresh(user)
    return user


def validate_ownership(db: Session, discord_id: str, item_id: int | None) -> int | None:
    if item_id is None:
        return None
    inv = (
        db.query(models_db.InventoryItem)
        .filter(models_db.InventoryItem.id == item_id, models_db.InventoryItem.discord_id == discord_id)
        .first()
    )
    if not inv:
        raise HTTPException(status_code=400, detail=f"Item {item_id} 不存在或不屬於此玩家")
    return item_id


@app.post("/api/users/{discord_id}/equipment", response_model=UserProfileOut, tags=["User"])
def update_equipment(discord_id: str, payload: UserEquipmentUpdate, db: Session = Depends(get_db)):
    user = ensure_user(db, discord_id)
    user.equip_weapon_id = validate_ownership(db, discord_id, payload.weapon_id)
    user.equip_shield_id = validate_ownership(db, discord_id, payload.shield_id)
    user.equip_armor_id = validate_ownership(db, discord_id, payload.armor_id)
    user.equip_cloak_id = validate_ownership(db, discord_id, payload.cloak_id)
    user.equip_head_id = validate_ownership(db, discord_id, payload.head_id)
    user.equip_ring_id = validate_ownership(db, discord_id, payload.ring_id)
    user.equip_acc1_id = validate_ownership(db, discord_id, payload.acc1_id)
    user.equip_acc2_id = validate_ownership(db, discord_id, payload.acc2_id)

    equipped_ids = [
        user.equip_weapon_id,
        user.equip_shield_id,
        user.equip_armor_id,
        user.equip_cloak_id,
        user.equip_head_id,
        user.equip_ring_id,
        user.equip_acc1_id,
        user.equip_acc2_id,
    ]
    equipped_ids = [i for i in equipped_ids if i]
    if equipped_ids:
        items = (
            db.query(models_db.InventoryItem)
            .options(joinedload(models_db.InventoryItem.item_template))
            .filter(models_db.InventoryItem.id.in_(equipped_ids))
            .all()
        )
    else:
        items = []

    def sum_stat(key: str) -> int:
        total = 0
        for it in items:
            tmpl = it.item_template
            if tmpl:
                total += int(getattr(tmpl, key, 0) or 0)
        return total

    user.stat_attack = sum_stat("stat_attack")
    user.stat_defense = sum_stat("stat_defense")
    user.stat_agility = sum_stat("stat_agility")
    user.stat_int = sum_stat("stat_intelligence")
    user.stat_luk = sum_stat("stat_luck")

    db.commit()
    db.refresh(user)
    return user_to_out(user)


@app.post("/api/wallet/topup", response_model=WalletOut, tags=["Wallet"])
def wallet_topup(payload: WalletTopupIn, db: Session = Depends(get_db)):
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="儲值金額需要 > 0")

    ensure_user(db, payload.discord_id)
    wallet = ensure_wallet(db, payload.discord_id)
    wallet.balance = wallet.balance + payload.amount

    db.commit()
    db.refresh(wallet)
    return wallet


@app.get("/api/wallet/{discord_id}", response_model=WalletOut, tags=["Wallet"])
def get_wallet(discord_id: str, db: Session = Depends(get_db)):
    wallet = (
        db.query(models_db.Wallet)
        .filter(models_db.Wallet.discord_id == discord_id)
        .first()
    )
    if not wallet:
        return WalletOut(discord_id=discord_id, balance=0, frozen_balance=0)
    return wallet


@app.post("/api/inventory/grant", response_model=InventoryItemOut, tags=["Inventory"])
def grant_item(payload: InventoryGrantIn, db: Session = Depends(get_db)):
    if payload.qty <= 0:
        raise HTTPException(status_code=400, detail="qty 必須大於 0")

    user = ensure_user(db, payload.discord_id)
    item_template = db.query(models_db.ItemTemplate).get(payload.item_template_id)
    if not item_template:
        raise HTTPException(status_code=404, detail="Item template not found")

    inv_item = (
        db.query(models_db.InventoryItem)
        .filter(
            models_db.InventoryItem.discord_id == user.discord_id,
            models_db.InventoryItem.item_template_id == payload.item_template_id,
        )
        .with_for_update()
        .first()
    )

    current_total = get_inventory_total_qty(db, user.discord_id)
    if current_total + payload.qty > BAG_CAPACITY:
        raise HTTPException(status_code=400, detail="背包容量不足")

    if not inv_item:
        inv_item = models_db.InventoryItem(
            discord_id=user.discord_id,
            item_template_id=payload.item_template_id,
            qty=payload.qty,
            note=payload.note,
        )
        db.add(inv_item)
    else:
        inv_item.qty = inv_item.qty + payload.qty
        if payload.note:
            inv_item.note = payload.note

    db.commit()
    db.refresh(inv_item)
    return inv_item


@app.get("/api/inventory/{discord_id}", response_model=List[InventoryItemOut], tags=["Inventory"])
def list_inventory(discord_id: str, db: Session = Depends(get_db)):
    user = db.get(models_db.UserProfile, discord_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    items = (
        db.query(models_db.InventoryItem)
        .filter(models_db.InventoryItem.discord_id == discord_id)
        .order_by(models_db.InventoryItem.acquired_at.desc())
        .all()
    )
    return items


@app.get("/api/inventory/{discord_id}/summary", response_model=InventorySummaryOut, tags=["Inventory"])
def get_inventory_summary(discord_id: str, db: Session = Depends(get_db)):
    user = db.get(models_db.UserProfile, discord_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    items = (
        db.query(models_db.InventoryItem)
        .filter(models_db.InventoryItem.discord_id == discord_id)
        .order_by(models_db.InventoryItem.acquired_at.desc())
        .all()
    )
    filtered = [it for it in items if int(it.qty or 0) > 0]
    total_qty = sum(int(it.qty or 0) for it in filtered)
    return InventorySummaryOut(discord_id=discord_id, total_qty=total_qty, capacity=BAG_CAPACITY, items=filtered)


# 技能類別 / 怪物
@app.post("/api/skill-categories", response_model=SkillCategoryOut, tags=["Monster"])
def create_skill_category(payload: SkillCategoryCreate, db: Session = Depends(get_db)):
    exists = (
        db.query(models_db.SkillCategory)
        .filter(models_db.SkillCategory.name == payload.name)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="技能類別已存在")

    category = models_db.SkillCategory(name=payload.name, description=payload.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@app.get("/api/skill-categories", response_model=List[SkillCategoryOut], tags=["Monster"])
def list_skill_categories(db: Session = Depends(get_db)):
    cats = db.query(models_db.SkillCategory).order_by(models_db.SkillCategory.id).all()
    return cats


@app.post("/api/monsters", response_model=MonsterOut, tags=["Monster"])
def create_monster(payload: MonsterCreate, db: Session = Depends(get_db)):
    categories: list[models_db.SkillCategory] = []
    if payload.skill_category_ids:
        categories = (
            db.query(models_db.SkillCategory)
            .filter(models_db.SkillCategory.id.in_(payload.skill_category_ids))
            .all()
        )
        found_ids = {c.id for c in categories}
        missing = [cid for cid in payload.skill_category_ids if cid not in found_ids]
        if missing:
            raise HTTPException(status_code=404, detail=f"技能類別不存在: {missing}")

    monster = models_db.Monster(
        name=payload.name,
        level=payload.level,
        area=payload.area,
        drop_items=json.dumps(payload.drop_items or []),
        attack=payload.attack,
        hp=payload.hp,
        defense=payload.defense,
    )
    monster.skill_categories = categories
    db.add(monster)
    db.commit()
    db.refresh(monster)
    return serialize_monster(monster)


@app.get("/api/monsters", response_model=List[MonsterOut], tags=["Monster"])
def list_monsters(db: Session = Depends(get_db)):
    monsters = (
        db.query(models_db.Monster)
        .options(joinedload(models_db.Monster.skill_categories))
        .order_by(models_db.Monster.level.asc(), models_db.Monster.id.asc())
        .all()
    )
    return [serialize_monster(m) for m in monsters]


@app.get("/api/monsters/{monster_id}", response_model=MonsterOut, tags=["Monster"])
def get_monster(monster_id: int, db: Session = Depends(get_db)):
    monster = (
        db.query(models_db.Monster)
        .options(joinedload(models_db.Monster.skill_categories))
        .get(monster_id)
    )
    if not monster:
        raise HTTPException(status_code=404, detail="怪物不存在")
    return serialize_monster(monster)


# Dungeons
@app.post("/api/dungeons", response_model=DungeonOut, tags=["Dungeon"])
def create_dungeon(payload: DungeonCreate, db: Session = Depends(get_db)):
    boss = None
    if payload.boss_id:
        boss = db.query(models_db.Monster).get(payload.boss_id)
        if not boss:
            raise HTTPException(status_code=404, detail="Boss 不存在")

    dungeon = models_db.Dungeon(
        name=payload.name,
        level_req=payload.level_req,
        difficulty=payload.difficulty,
        icon=payload.icon,
        boss_id=payload.boss_id,
    )
    db.add(dungeon)
    db.commit()
    db.refresh(dungeon)
    if boss:
        dungeon.boss = boss
    return serialize_dungeon(dungeon)


@app.get("/api/dungeons", response_model=List[DungeonOut], tags=["Dungeon"])
def list_dungeons(db: Session = Depends(get_db)):
    dungeons = (
        db.query(models_db.Dungeon)
        .options(joinedload(models_db.Dungeon.boss).joinedload(models_db.Monster.skill_categories))
        .order_by(models_db.Dungeon.level_req.asc(), models_db.Dungeon.id.asc())
        .all()
    )
    return [serialize_dungeon(d) for d in dungeons]


@app.get("/api/dungeons/{dungeon_id}", response_model=DungeonOut, tags=["Dungeon"])
def get_dungeon(dungeon_id: int, db: Session = Depends(get_db)):
    dungeon = (
        db.query(models_db.Dungeon)
        .options(joinedload(models_db.Dungeon.boss).joinedload(models_db.Monster.skill_categories))
        .get(dungeon_id)
    )
    if not dungeon:
        raise HTTPException(status_code=404, detail="Dungeon 不存在")
    return serialize_dungeon(dungeon)
