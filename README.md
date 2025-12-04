# RPG 裝備交易平台 — 遊戲產品企劃書

## 1. 核心概念
- 類型：RPG 打怪 + 裝備收集 + 玩家交易所。
- 目標：透過刷副本、擊敗怪物取得裝備與素材，並在市場自由掛單 / 吃單交易。
- 核心循環：戰鬥 → 掉落 → 強化 / 交易 → 成長 → 挑戰更高難度。

## 2. 核心玩法
- **戰鬥 / 副本**
  - 地城分等級與難度，含小怪與 BOSS。
  - 怪物掉落對應的道具模板，掉落率、數量可配置。
- **角色成長**
  - 角色等級、經驗；升級給能力點（可分配攻擊/防禦/敏捷/智力/幸運）。
  - 裝備欄：武器 / 盾牌 / 鎧甲 / 披風 / 頭飾 / 戒指 / 飾品1 / 飾品2。
  - 能力點分配帶來基礎屬性提升，裝備則提供加成。
- **交易所**
  - 玩家可掛 BUY/SELL 單，價格撮合（同價、時間優先），禁止自成交。
  - 成交後自動處理凍結資金 / 保證金與庫存變動，生成交易記錄。
  - 成交經驗：成交價值 × 1%，至少 1 點，買賣雙方皆得。

## 3. 經濟與數值
- **經驗與升級**
  - 等級需求：`LEVEL_EXP_TABLE`，超出表長後以最後一級需求逐級 ×1.5。
  - 成交經驗：`(價格 × 數量) × TRADE_EXP_RATE (預設 1%)`，取整且至少 1。
  - 戰鬥經驗：依副本 / 怪物配置（可拓展）。
  - 升級獎勵：每級給 `LEVEL_UP_STAT_POINTS`（預設 1 或依需求調整）。
- **貨幣**
  - 初始錢包：註冊即送 100（Zeny）。
  - 錢包欄位：可用、凍結；下單/成交會自動凍結與解凍。
  - 背包容量：預設 500，可調。
- **道具**
  - 道具模板：稀有度、槽位、初始價格與各項屬性。
  - 怪物掉落：配置 `drop_rate`、`qty_min`、`qty_max` 與對應模板。

## 4. 介面與流程（前端概要）
- **首頁**：英雄區、公告（readme.txt）、最新掛單跑馬燈。
- **登入/註冊**：平台或 Discord（模擬）；登入後取得 Bearer Token。
- **個人中心**：
  - 顯示等級/經驗（後端回傳 `next_exp_needed`）、未分配能力點、角色屬性。
  - 分配能力點彈窗，呼叫 `/api/users/{id}/allocate-points`。
  - 背包與裝備欄顯示。
- **地城頁**：
  - 列出地城、選怪戰鬥、顯示掉落並自動寫入背包（呼叫 `/api/inventory/grant`）。
- **市場頁**：
  - 道具選單、K 線（Lightweight Charts）、訂單簿、下單/取消、我的掛單、背包摘要。
  - EXP 進度顯示 `exp / next_exp_needed`。

## 5. API 主要端點（摘錄）
- 認證：`POST /api/auth/register`、`POST /api/auth/login`（回傳 TokenOut）。
- 用戶：`GET /api/users/{id}`、`POST /api/users/upsert`、`POST /api/users/add-exp`、`POST /api/users/{id}/allocate-points`、`POST /api/users/{id}/equipment`。
- 錢包：`GET /api/wallet/{id}`、`POST /api/wallet/topup`。
- 庫存：`GET /api/inventory/{id}`、`GET /api/inventory/{id}/summary`、`POST /api/inventory/grant`。
- 道具模板：CRUD（示例：`POST /api/item-templates`、`GET /api/item-templates`）。
- 訂單與撮合：`POST /api/orders`、`GET /api/orderbook/{item_template_id}`、`POST /api/orders/{id}/cancel?discord_id=...`。
- 交易紀錄：`GET /api/trades/{item_template_id}`。
- 地城 / 怪物：`GET/POST /api/dungeons`、`POST /api/dungeons/{id}/monsters`、`GET/POST /api/monsters`、`POST /api/monsters/{monster_id}/drops`。

## 6. 權杖與安全
- 所有需要登入的操作（下單、錢包、背包、分配能力點等）必須帶 `Authorization: Bearer <token>`。
- `/api/inventory/grant` 等保護路由未帶 token 會回 401。

## 7. 待辦與延伸
- 道具強化 / 鍛造系統（素材合成、失敗率、保護道具）。
- 副本多階段與隊伍協作機制。
- 更細緻的稀有度與詞綴系統。
- 交易費用與稅率配置，拍賣行冷卻。
- 排行榜（戰力、財富、成交量）、成就與每日任務。
- 更豐富的公告 / 活動配置（可讀取外部 JSON/MD）。

## 8. 部署與啟動（開發）
- 後端：`uvicorn server.app.main:app --reload --host 127.0.0.1 --port 8000`
- Swagger：`http://127.0.0.1:8000/docs`
- 前端：直接以靜態檔案方式開啟 `server/app/*.html`，或使用本機伺服器提供。
