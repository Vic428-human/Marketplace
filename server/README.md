README.md
# 後端架構


├─ app/
│  ├─ main.py          # FastAPI 入口
│  ├─ deps.py          # 共用依賴（例如 firebase client）
│  ├─ models.py        # Pydantic 資料模型
├─ firebase-key.json   # Firebase service account 金鑰（不要 commit）
├─ requirements.txt