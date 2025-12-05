from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
import requests
import uuid

# -----------------------
# 資料模型定義
# -----------------------

class Material(BaseModel):
    id: str
    name: str
    element: Optional[str] = None   # fire / water / dark ...
    grade: Optional[str] = None     # S / A / B ...

class Constraints(BaseModel):
    max_main_stat: int = 9999
    max_sub_stats: int = 4
    allowed_elements: Optional[List[str]] = None
    banned_keywords: Optional[List[str]] = None

class SynthesisRequest(BaseModel):
    player_id: str
    player_level: int
    lang: Literal["zh-TW", "en"] = "zh-TW"
    target_type: Literal["weapon", "armor", "accessory"] = "weapon"
    rarity: Literal["N", "R", "SR", "SSR", "UR"] = "SR"
    materials: List[Material]
    constraints: Constraints
    seed: Optional[int] = None

class Stat(BaseModel):
    name: str
    value: float

class SpecialEffect(BaseModel):
    code: str
    name: str
    description: str

class GeneratedItem(BaseModel):
    item_id: str
    name: str
    type: str
    rarity: str
    element: Optional[str]
    level_requirement: int
    main_stat: Stat
    sub_stats: List[Stat]
    special_effect: SpecialEffect
    flavor_text: str
    meta: Dict[str, Any]

# -----------------------
# FastAPI app
# -----------------------

app = FastAPI(title="Game Synthesis AI (Ollama)")

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "qwen2.5:3b"  # 你剛剛 pull 的模型名字

SYSTEM_PROMPT = """
你是一個 RPG 遊戲設計AI，專門產生「裝備合成結果」。

請嚴格遵守：
1. 只輸出 JSON，不要有任何多餘文字或註解。
2. 必須符合我稍後給你的 JSON Schema 欄位與型別。
3. 主屬性與副屬性數值不可超過 constraints 裡的上限。
4. 名稱與描述須符合元素與稀有度，有世界觀感，但不得涉及色情、政治、現實金錢等。
5. special_effect.code 使用英文大寫與底線，如：FIRE_DARK_EXECUTE。
6. 當 lang=zh-TW 時，所有文字(名稱、描述、flavor_text)請使用繁體中文；當 lang=en 則使用英文。
"""

def build_user_prompt(req: SynthesisRequest) -> str:
    materials_desc = "\n".join(
        [f"- {m.name} (id={m.id}, element={m.element}, grade={m.grade})"
         for m in req.materials]
    )

    allowed_elements = (
        ", ".join(req.constraints.allowed_elements)
        if req.constraints.allowed_elements else "不限"
    )
    banned_keywords = (
        ", ".join(req.constraints.banned_keywords)
        if req.constraints.banned_keywords else "無"
    )

    # 這裡把我們的 JSON Schema 描述給模型看
    schema_desc = """
你必須輸出一個 JSON，欄位如下 (請不要漏掉)：

{
  "item_id": string,              // 唯一ID，可隨意生成
  "name": string,                 // 裝備名稱
  "type": string,                 // weapon / armor / accessory 等
  "rarity": string,               // N / R / SR / SSR / UR
  "element": string | null,       // 元素，如 "fire", "water", "dark" 或組合
  "level_requirement": int,       // 裝備需求等級
  "main_stat": {
    "name": string,               // 例如 "攻擊力"
    "value": number               // 數值，不可超過 max_main_stat
  },
  "sub_stats": [                  // 最多 max_sub_stats 條
    { "name": string, "value": number }
  ],
  "special_effect": {
    "code": string,               // 例如 "FIRE_DARK_EXECUTE"
    "name": string,               // 特效名稱
    "description": string         // 效果描述
  },
  "flavor_text": string,          // 世界觀風味文本
  "meta": {
    "seed": number | null,
    "generated_by": string,
    "safety_filtered": boolean
  }
}
"""

    lang_desc = "繁體中文" if req.lang == "zh-TW" else "英文"

    prompt = f"""
玩家資訊：
- 玩家ID：{req.player_id}
- 玩家等級：{req.player_level}

合成目標：
- 類型：{req.target_type}
- 期望稀有度：{req.rarity}
- 語言：{lang_desc}

素材列表：
{materials_desc}

屬性限制：
- 主屬性最大值：{req.constraints.max_main_stat}
- 副屬性最多條數：{req.constraints.max_sub_stats}
- 可用元素：{allowed_elements}
- 禁用關鍵字：{banned_keywords}

隨機種子 (若有)：{req.seed}

請依照上述資訊，依照以下 JSON Schema 嚴格輸出一個完整的 JSON：
{schema_desc}
"""
    return prompt


@app.post("/api/synthesis", response_model=GeneratedItem)
def create_synthesis(req: SynthesisRequest):
    user_prompt = build_user_prompt(req)

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama 連線失敗: {e}")

    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Ollama 錯誤: {resp.text}")

    data = resp.json()
    # Ollama /api/chat 回傳格式 => { "message": { "role": "...", "content": "LLM輸出文字" }, ... }
    content = data.get("message", {}).get("content", "").strip()

    # 有些模型偶爾會在 JSON 前後加 ```json ```，這裡粗暴清一下
    if content.startswith("```"):
        content = content.strip("`")
        content = content.replace("json", "", 1).strip()

    import json
    try:
        obj = json.loads(content)
    except json.JSONDecodeError as e:
        # 方便 debug：把 model 回傳內容也帶出去
        raise HTTPException(
            status_code=500,
            detail=f"AI 回傳的不是合法 JSON，錯誤: {e}. 原始內容: {content[:300]}"
        )

    # 如果 item_id 沒給，就自動補一個
    if "item_id" not in obj or not obj["item_id"]:
        obj["item_id"] = f"gen_{uuid.uuid4().hex[:12]}"

    # 補上 meta 欄位的一些資訊
    meta = obj.get("meta", {})
    meta.setdefault("seed", req.seed)
    meta.setdefault("generated_by", MODEL_NAME)
    meta.setdefault("safety_filtered", True)
    obj["meta"] = meta

    return GeneratedItem(**obj)
