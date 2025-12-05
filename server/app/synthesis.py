from typing import List, Optional, Literal, Dict, Any
import requests
import json
import uuid
import random
from sqlalchemy.orm import Session
from opencc import OpenCC # Import OpenCC

SYNTHESIS_SUCCESS_RATE = 0.8  # 80% chance of success

# Initialize OpenCC for Simplified to Traditional Chinese conversion
cc = OpenCC('s2t') 


from pydantic import BaseModel, Field # Import Field here
from . import models_db # Assuming models_db is in the same directory

# -----------------------
# 資料模型定義 (從 llm.py 複製而來)
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
    target_type: Literal["weapon", "shield", "armor", "head", "ring", "accessory", "misc"] = "weapon" # Expanded types
    rarity: Literal["N", "R", "SR", "SSR", "UR"] = "SR"
    materials: List[Material]
    constraints: Constraints
    seed: Optional[int] = None

class Stat(BaseModel):
    name: str
    value: float

class SpecialEffect(BaseModel):
    code: str
    name: Optional[str] = None
    description: Optional[str] = None

class GeneratedItem(BaseModel):
    item_id: str
    name: str
    type: Literal["weapon", "shield", "armor", "head", "ring", "accessory", "misc"] # Expanded types
    rarity: Literal["N", "R", "SR", "SSR", "UR"]
    element: Optional[str]
    level_requirement: int
    main_stat: Stat
    sub_stats: List[Stat]
    special_effect: SpecialEffect
    flavor_text: str
    meta: Dict[str, Any]

# -----------------------
# Ollama 配置與提示 (從 llm.py 複製而來)
# -----------------------

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "qwen2.5:7b"  # 使用者指定的模型

SYSTEM_PROMPT = """
你是一個 RPG 遊戲設計AI，專門產生「裝備合成結果」。

請嚴格遵守：
1. 只輸出 JSON，不要有任何多餘文字或註解。
2. 必須符合我稍後給你的 JSON Schema 欄位與型別。
3. 主屬性與副屬性 (main_stat, sub_stats) 的 value 數值必須嚴格介於 1 到 5 之間。
4. 名稱與描述須符合元素與稀有度，有世界觀感，但不得涉及色情、政治、現實金錢等。
5. special_effect.code 使用英文大寫與底線，如：FIRE_DARK_EXECUTE。
6. 當 lang=zh-TW 時，所有文字(名稱、描述、flavor_text)請使用繁體中文；當 lang=en 則使用英文。
7. 裝備名稱 (name) 欄位，絕對不可以使用任何 emoji 表情符號。
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
  "type": "weapon" | "shield" | "armor" | "head" | "ring" | "accessory" | "misc", // 裝備類型
  "rarity": "N" | "R" | "SR" | "SSR" | "UR", // 稀有度
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
    "name": string | null,        // 特效名稱
    "description": string | null  // 效果描述
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

# -----------------------
# 合成邏輯 (重寫)
# -----------------------

async def synthesize_item_async(input_item_templates: List[models_db.ItemTemplate], db: Session, current_user_discord_id: str, current_user_level: int) -> models_db.ItemTemplate:
    """
    Handles the item synthesis process by calling a local Ollama model (via requests).
    """
    # Simulate synthesis failure based on success rate
    if random.random() > SYNTHESIS_SUCCESS_RATE:
        raise ValueError("合成失敗，你的材料已消失在虛空中！")

    if not input_item_templates:
        raise ValueError("Synthesis requires at least one input item.")

    # 1. 準備 SynthesisRequest
    materials_for_ollama = [
        Material(
            id=str(item.id),
            name=item.name,
            element=item.slot_type, # Using slot_type as a proxy for element
            grade=item.rarity # Using rarity as a proxy for grade
        )
        for item in input_item_templates
    ]

    # 簡單推斷合成物品的類型和稀有度
    # 可以根據實際需求設計更複雜的推斷邏輯
    target_type_counts = {}
    rarity_counts = {}
    for item in input_item_templates:
        target_type_counts[item.slot_type] = target_type_counts.get(item.slot_type, 0) + 1
        rarity_counts[item.rarity] = rarity_counts.get(item.rarity, 0) + 1
    
    # 取最多的類型作為合成目標類型 (從數據庫類型轉化為 GeneratedItem 的 Literal)
    # 預設為 "weapon"
    target_type = "weapon"
    if target_type_counts:
        inferred_type = max(target_type_counts, key=target_type_counts.get).lower()
        if inferred_type in ["weapon", "shield", "armor", "head", "ring", "accessory", "misc"]:
            target_type = inferred_type
    
    # 取最高的稀有度作為期望稀有度 (從數據庫類型轉化為 GeneratedItem 的 Literal)
    # 預設為 "N"
    target_rarity = "N"
    if rarity_counts:
        inferred_rarity_db_format = max(rarity_counts, key=rarity_counts.get).upper()
        # 轉換為 GeneratedItem.rarity 的 Literal 格式
        db_rarity_to_ollama_rarity = {
            "COMMON": "N",
            "UNCOMMON": "R",
            "RARE": "SR",
            "EPIC": "SSR",
            "LEGENDARY": "UR"
        }
        target_rarity = db_rarity_to_ollama_rarity.get(inferred_rarity_db_format, "N")


    synthesis_req_payload = SynthesisRequest(
        player_id=current_user_discord_id,
        player_level=current_user_level,
        lang="zh-TW", # Hardcode for now, could be dynamic
        target_type=target_type,
        rarity=target_rarity,
        materials=materials_for_ollama,
        constraints=Constraints(), # Default constraints for now
        seed=None
    )

    # 2. 建立使用者提示
    user_prompt = build_user_prompt(synthesis_req_payload)

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False # We want a single response
    }

    # 3. 呼叫 Ollama API
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(f"Ollama 連線失敗: {e}. 請確認 Ollama 服務正在運行且模型 '{MODEL_NAME}' 已下載。")
    except Exception as e:
        raise ConnectionError(f"呼叫 Ollama 服務時發生未知錯誤: {e}")

    if resp.status_code != 200:
        raise ConnectionError(f"Ollama 服務回傳錯誤 (狀態碼: {resp.status_code}): {resp.text}")

    data = resp.json()
    content = data.get("message", {}).get("content", "").strip()
    print('=======content:',content)

    # 有些模型偶爾會在 JSON 前後加 ```json ```，這裡粗暴清一下
    if content.startswith("```"):
        content = content.strip("`")
        content = content.replace("json", "", 1).strip()

    # 4. 解析 JSON 回覆
    try:
        generated_item_data = json.loads(content)
        # 補上 meta 欄位的一些資訊 (從 llm.py 複製)
        meta = generated_item_data.get("meta", {})
        meta.setdefault("seed", synthesis_req_payload.seed)
        meta.setdefault("generated_by", MODEL_NAME)
        meta.setdefault("safety_filtered", True)
        generated_item_data["meta"] = meta

        # 驗證並創建 GeneratedItem Pydantic 模型
        generated_item = GeneratedItem(**generated_item_data)

        # If the item is 'misc', ensure it has no stats as per user's requirement.
        if generated_item.type == "misc":
            generated_item.main_stat.value = 0
            generated_item.sub_stats = []

        # Convert all relevant text fields to Traditional Chinese
        generated_item.name = cc.convert(generated_item.name)
        generated_item.flavor_text = cc.convert(generated_item.flavor_text)
        if generated_item.special_effect.name:
            generated_item.special_effect.name = cc.convert(generated_item.special_effect.name)
        if generated_item.special_effect.description:
            generated_item.special_effect.description = cc.convert(generated_item.special_effect.description)

    except json.JSONDecodeError as e:
        raise ValueError(f"Ollama 回傳的不是合法 JSON，錯誤: {e}. 原始內容: {content[:500]}...")
    except Exception as e:
        raise ValueError(f"解析 Ollama 回覆失敗: {e}. 原始內容: {content[:500]}...")


    # 5. 轉換為 models_db.ItemTemplate 並儲存
    # 將 GeneratedItem.rarity (N, R, SR, SSR, UR) 轉換為 models_db.ItemTemplate.rarity (COMMON, UNCOMMON, RARE, EPIC, LEGENDARY)
    rarity_ollama_to_db = {
        "N": "COMMON",
        "R": "UNCOMMON",
        "SR": "RARE",
        "SSR": "EPIC",
        "UR": "LEGENDARY"
    }
    
    # 將 GeneratedItem.type 轉換為 models_db.ItemTemplate.slot_type
    # 這裡假設 GeneratedItem.type 會直接與 models_db.ItemTemplate.slot_type 的大寫形式匹配
    # 例如 "weapon" -> "WEAPON"
    
    new_item_template = models_db.ItemTemplate(
        name=generated_item.name,
        description=f"{generated_item.flavor_text}\n\n特殊效果: {generated_item.special_effect.name if generated_item.special_effect.name else '無' } - {generated_item.special_effect.description if generated_item.special_effect.description else '無'}",
        rarity=rarity_ollama_to_db.get(generated_item.rarity, "COMMON"), # 使用轉換後的稀有度
        slot_type=generated_item.type.upper(), # 直接使用轉換後的大寫類型
        initial_price=0, # 初始價格為 0，可後續設定
        stat_attack=int(generated_item.main_stat.value if generated_item.main_stat.name == "攻擊力" else 0),
        stat_defense=int(generated_item.main_stat.value if generated_item.main_stat.name == "防禦力" else 0),
        stat_agility=int(generated_item.main_stat.value if generated_item.main_stat.name == "敏捷" else 0),
        stat_intelligence=int(generated_item.main_stat.value if generated_item.main_stat.name == "智力" else 0),
        stat_luck=int(generated_item.main_stat.value if generated_item.main_stat.name == "幸運" else 0),
        is_generated=True
    )
    
    # 處理 sub_stats
    for sub_stat in generated_item.sub_stats:
        if sub_stat.name == "攻擊力":
            new_item_template.stat_attack += int(sub_stat.value)
        elif sub_stat.name == "防禦力":
            new_item_template.stat_defense += int(sub_stat.value)
        elif sub_stat.name == "敏捷":
            new_item_template.stat_agility += int(sub_stat.value)
        elif sub_stat.name == "智力":
            new_item_template.stat_intelligence += int(sub_stat.value)
        elif sub_stat.name == "幸運":
            new_item_template.stat_luck += int(sub_stat.value)

    db.add(new_item_template)
    db.flush()
    db.refresh(new_item_template)

    return new_item_template