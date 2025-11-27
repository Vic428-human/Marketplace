# app/main.py
from fastapi import FastAPI,HTTPException
from typing import List
from contextlib import asynccontextmanager

from .deps import get_firestore_client
from .models import CreateSellItem, ProductDB
from datetime import datetime, timezone



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 FastAPI Starting...")
    get_firestore_client()
    print("🔥 Firestore Initialized")

    yield

    print("🛑 FastAPI Shutdown...")

app = FastAPI(lifespan=lifespan,title="Ro Trade API Serverr",
    description="RO 交易平台後端 API",
    version="1.0.0",)

# =====================================================
# 1. 建立商品
# =====================================================
@app.post("/api/createItem", response_model=ProductDB)
def create_item(itemInfo: CreateSellItem):
    db = get_firestore_client()
    doc_ref = db.collection("itemID").document()  # 自動產 ID

    now = datetime.now(timezone.utc)

    data = itemInfo.model_dump()
    data["created_at"] = now
    data["updated_at"] = now
    print(data)
    doc_ref.set(data)  # Firestore 要 dict

    # 這裡的 data 已經包含 created_at / updated_at
    return ProductDB(id=doc_ref.id, **data)

# =====================================================
# 2. 查詢單筆 item（依 ID）
# =====================================================
@app.get("/api/item/{item_id}", response_model=ProductDB)
def get_item(item_id: str):
    db = get_firestore_client()
    doc = db.collection("itemID").document(item_id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Item not found")

    data = doc.to_dict()
    return ProductDB(id=doc.id, **data)

# =====================================================
# 3. 查全部 item
# =====================================================
@app.get("/api/items", response_model=List[ProductDB])
def list_items():
    db = get_firestore_client()
    docs = db.collection("itemID").stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append(ProductDB(id=doc.id, **data))

    return results
    
# =====================================================
# 4. 依 userID 查詢 item
# =====================================================
@app.get("/api/items/user/{user_id}", response_model=List[ProductDB])
def list_items_by_user(user_id: str):
    db = get_firestore_client()
    query = db.collection("itemID").where("userID", "==", user_id)
    docs = query.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append(ProductDB(id=doc.id, **data))

    return results


# =====================================================
# 5. 依 itemType 查詢（1=收購 2=出售）
# =====================================================
@app.get("/api/items/type/{item_type}", response_model=List[ProductDB])
def list_items_by_type(item_type: int):
    db = get_firestore_client()
    query = db.collection("itemID").where("itemType", "==", item_type)
    docs = query.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append(ProductDB(id=doc.id, **data))

    return results


# =====================================================
# 6. 複合查詢（userID + itemType）
# =====================================================
@app.get("/api/items/search", response_model=List[ProductDB])
def search_items(userID: str, itemType: int):
    db = get_firestore_client()
    query = db.collection("itemID")\
              .where("userID", "==", userID)\
              .where("itemType", "==", itemType)

    docs = query.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append(ProductDB(id=doc.id, **data))

    return results