# app/deps.py
import os
import firebase_admin
from firebase_admin import credentials, firestore

from functools import lru_cache

osPath = os.path.abspath(os.path.join(os.getcwd(), "."))
@lru_cache
def get_firestore_client():
    # 建議改成從環境變數讀路徑
    cred = credentials.Certificate(osPath + "//rotrade-783e7-firebase-adminsdk-fbsvc-a451bc525c.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    return db

