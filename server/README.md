```
README.md
# 後端架構


├─ app/

│  ├─ main.py          # FastAPI 入口

│  ├─ deps.py          # 共用依賴（例如 firebase client）

│  ├─ models.py        # Pydantic 資料模型

├─ requirements.txt
```


INSERT INTO skill_categories ...（若需要技能類別）
INSERT INTO item_templates ...（掉落的裝備模板）
INSERT INTO monsters ...（怪物本體）
INSERT INTO monster_skill_categories ...（怪物技能類別）
INSERT INTO monster_drops ...（怪物掉落機率）
INSERT INTO dungeons (name, level_req, difficulty, icon, boss_id) ...（Boss 要已存在）