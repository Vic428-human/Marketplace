"""
高速隨機掛單 / 自成交 bot
- 支援多個 bot 身份，預設 3 個，會輪流上下單、偶爾同價買賣強制成交，讓 K 線持續有波動。
- 先為每個 bot：upsert 用戶、儲值、發放背包，避免餘額/庫存不足。

環境變數（可調整）：
  API_BASE   預設 http://127.0.0.1:8000
  NUM_BOTS   預設 3
  TOPUP      預設 50000
  GRANT_QTY  預設 200
  ITEM_ID    預設 1
  MIN_P      最低價格，預設 100
  MAX_P      最高價格，預設 2000
  MAX_QTY    單筆最大數量，預設 3
  CROSS_RATE 自成交機率，預設 0.6（60%）
  SLEEP_MIN  最短間隔秒，預設 0.5
  SLEEP_MAX  最長間隔秒，預設 2.0
"""
import os
import random
import time
from dataclasses import dataclass

import requests


API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")
NUM_BOTS = int(os.environ.get("NUM_BOTS", "3"))
ITEM_TEMPLATE_ID = int(os.environ.get("ITEM_ID", "1"))
TOPUP_AMOUNT = float(os.environ.get("TOPUP", "50000"))
GRANT_QTY = int(os.environ.get("GRANT_QTY", "200"))
MIN_PRICE = int(os.environ.get("MIN_P", "1000"))
MAX_PRICE = int(os.environ.get("MAX_P", "2000"))
MAX_QTY = int(os.environ.get("MAX_QTY", "3"))
CROSS_RATE = float(os.environ.get("CROSS_RATE", "0.6"))
SLEEP_MIN = float(os.environ.get("SLEEP_MIN", "0.5"))
SLEEP_MAX = float(os.environ.get("SLEEP_MAX", "2.0"))

HEADERS = {"ngrok-skip-browser-warning": "true"}


@dataclass
class BotUser:
    discord_id: str
    discord_name: str


def call(method: str, path: str, json=None):
    url = f"{API_BASE}{path}"
    resp = requests.request(method, url, json=json, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    if resp.content:
        return resp.json()
    return None


def bootstrap_bot(bot: BotUser):
    call("POST", "/api/users/upsert", {"discord_id": bot.discord_id, "discord_name": bot.discord_name})
    call("POST", "/api/wallet/topup", {"discord_id": bot.discord_id, "amount": TOPUP_AMOUNT})
    call(
        "POST",
        "/api/inventory/grant",
        {
            "discord_id": bot.discord_id,
            "item_template_id": ITEM_TEMPLATE_ID,
            "qty": GRANT_QTY,
            "note": f"bot grant {bot.discord_name}",
        },
    )
    print(f"[boot] {bot.discord_id} topup={TOPUP_AMOUNT} grant={GRANT_QTY}")


def place_order(bot: BotUser, side: str, price: float, qty: int):
    payload = {
        "discord_id": bot.discord_id,
        "discord_name": bot.discord_name,
        "item_template_id": ITEM_TEMPLATE_ID,
        "side": side,
        "price": price,
        "qty": qty,
        "note": "bot",
    }
    res = call("POST", "/api/orders", payload)
    print(f"[order] {bot.discord_name} {side} {price} x {qty} -> {res['id']}")


def place_cross(bot_a: BotUser, bot_b: BotUser, price: float, qty: int):
    # 先賣後買，強制成交
    place_order(bot_a, "SELL", price, qty)
    place_order(bot_b, "BUY", price, qty)
    print(f"[cross] {bot_a.discord_name}->{bot_b.discord_name} {price} x {qty}")


def random_bot_pool(n: int):
    bots = []
    for i in range(n):
        bots.append(BotUser(discord_id=f"BOT{i+1:03d}", discord_name=f"Bot{i+1:03d}"))
    return bots


def main():
    bots = random_bot_pool(NUM_BOTS)
    for b in bots:
        bootstrap_bot(b)

    while True:
        try:
            price = random.randint(MIN_PRICE, MAX_PRICE)
            qty = random.randint(1, MAX_QTY)
            if random.random() < CROSS_RATE:
                a, b = random.sample(bots, 2 if len(bots) >= 2 else 1)
                # 若不足兩個 bot，就同一個 bot 買賣
                bot_sell = a
                bot_buy = b if len(bots) >= 2 else a
                place_cross(bot_sell, bot_buy, price, qty)
            else:
                bot = random.choice(bots)
                side = random.choice(["BUY", "SELL"])
                place_order(bot, side, price, qty)
        except Exception as e:
            print("[fail]", e)
        time.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))


if __name__ == "__main__":
    main()
