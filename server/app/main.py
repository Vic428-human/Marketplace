# app/main.py
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import models_db  # 確保先匯入 models，讓 Base.metadata 能讀到表定義
from .db import Base, engine, get_db
from .schemas import OrderCreate, OrderOut,ItemTemplateCreate,ItemTemplateOut,WalletTopupIn, WalletOut

from typing import List
from fastapi.middleware.cors import CORSMiddleware
from decimal import Decimal

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 服務啟動時建表；第一次會建立，之後僅確認已存在
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Virtual Item Exchange",
    lifespan=lifespan,
)

# 👇 開發階段先允許全部來源，之後再鎖
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 可以改成 ["http://127.0.0.1:5500"] 之類
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 建立道具模板
@app.post("/api/item-templates", response_model=ItemTemplateOut, tags=["Item"])
def create_item_template(payload: ItemTemplateCreate, db: Session = Depends(get_db)):
    item = models_db.ItemTemplate(
        name=payload.name,
        game=payload.game,
        rarity=payload.rarity,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# 列出所有道具模板（方便查 id）
@app.get("/api/item-templates", response_model=List[ItemTemplateOut], tags=["Item"])
def list_item_templates(db: Session = Depends(get_db)):
    print(db)
    items = db.query(models_db.ItemTemplate).order_by(models_db.ItemTemplate.id).all()
    return items

# 建立訂單
@app.post("/api/orders", response_model=OrderOut, tags=["Order"])
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    item = db.query(models_db.ItemTemplate).get(payload.item_template_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item template not found")

    # 下單金額（簡單版：price * qty）
    required_amount = Decimal(payload.price) * Decimal(payload.qty)

    # BEGIN TRANSACTION
    try:
        # 1. 取得 / 建立錢包（for UPDATE）
        wallet = (
            db.query(models_db.Wallet)
            .filter(models_db.Wallet.discord_id == payload.discord_id)
            .with_for_update()
            .first()
        )
        if not wallet:
            # 沒錢包就視為 0 餘額
            wallet = models_db.Wallet(
                discord_id=payload.discord_id,
                balance=0,
                frozen_balance=0,
            )
            db.add(wallet)
            db.flush()  # 先寫進 session

        # 2. 計算可用餘額
        available = wallet.balance - wallet.frozen_balance

        if payload.side == "BUY":
            # 買單要有足夠保證金
            if available < required_amount:
                raise HTTPException(status_code=400, detail="餘額不足，無法掛買單")
            wallet.frozen_balance = wallet.frozen_balance + required_amount
            locked_amount = required_amount

        elif payload.side == "SELL":
            # 你說是「虛對虛」，不檢查背包數量
            # 可以選擇：
            # - 不凍結任何東西 locked_amount = 0
            # - 或者只凍結一點保證金，例如 10% 當 spam 保證金：
            deposit = required_amount * Decimal("0.1")
            if available < deposit:
                raise HTTPException(status_code=400, detail="餘額不足，無法掛賣單（保證金不足）")
            wallet.frozen_balance = wallet.frozen_balance + deposit
            locked_amount = deposit
        else:
            raise HTTPException(status_code=400, detail="side 必須為 BUY 或 SELL")

        # 3. 建立訂單
        order = models_db.Order(
            discord_id=payload.discord_id,
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
        db.commit()
        db.refresh(order)
        return order

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise

@app.get("/api/orderbook/{item_template_id}", response_model=List[OrderOut], tags=["Order"])
def get_orderbook(item_template_id: int, side: str | None = None, db: Session = Depends(get_db)):
    # 檢查道具是否存在（可選，但建議）
    item = db.query(models_db.ItemTemplate).get(item_template_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item template not found")

    query = db.query(models_db.Order).filter(
        models_db.Order.item_template_id == item_template_id,
        models_db.Order.status == "OPEN",
    )

    if side in ("BUY", "SELL"):
        query = query.filter(models_db.Order.side == side)

    # 賣單：價格由低到高；買單：價格由高到低
    if side == "SELL":
        query = query.order_by(models_db.Order.price.asc())
    elif side == "BUY":
        query = query.order_by(models_db.Order.price.desc())
    else:
        query = query.order_by(models_db.Order.created_at.desc())

    orders = query.all()
    return orders

@app.get("/api/orders/by-user/{discord_id}", response_model=List[OrderOut], tags=["Order"])
def get_orders_by_user(discord_id: str, db: Session = Depends(get_db)):
    orders = (
        db.query(models_db.Order)
        .filter(models_db.Order.discord_id == discord_id)
        .order_by(models_db.Order.created_at.desc())
        .all()
    )
    return orders


#除值
@app.post("/api/wallet/topup", response_model=WalletOut, tags=["Wallet"])
def wallet_topup(payload: WalletTopupIn, db: Session = Depends(get_db)):
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="儲值金額必須 > 0")

    wallet = (
        db.query(models_db.Wallet)
        .filter(models_db.Wallet.discord_id == payload.discord_id)
        .first()
    )

    if not wallet:
        wallet = models_db.Wallet(
            discord_id=payload.discord_id,
            balance=payload.amount,
            frozen_balance=0,
        )
        db.add(wallet)
    else:
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
        # 沒錢包就回 0，方便前端顯示
        return WalletOut(discord_id=discord_id, balance=0, frozen_balance=0)
    return wallet