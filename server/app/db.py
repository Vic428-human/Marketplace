# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 對應 docker-compose 裡的資料庫設定
DATABASE_URL = "postgresql+psycopg2://item_user:item_pass@localhost:5432/item_db"


class Base(DeclarativeBase):
    pass


# 開發時設定 echo=True，方便觀察實際執行的 SQL
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
        print(db)
    finally:
        db.close()
