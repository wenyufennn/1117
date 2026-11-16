# backend/app/database.py

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
# -------------------------------------------------
# ★ 請把下面的資訊改成您自己的資料庫設定 ★
# -------------------------------------------------
PG_USER = "postgres"          # ← 您的 PostgreSQL 使用者
PG_PASSWORD = "BX101240es"             # ← 若有密碼請填入，若無則留空
HOST = "localhost"
PORT = 5432
DB_NAME = "se1117"
# 建立完整的 URL（省略密碼時保留空的冒號部分即可）
if PG_PASSWORD:
    DATABASE_URL = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
else:
    DATABASE_URL = f"postgresql+asyncpg://{PG_USER}@{HOST}:{PORT}/{DB_NAME}"
# -------------------------------------------------
# 建立 async engine（echo=True 會在 console 印出 SQL，開發階段建議保留）
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)
# 為每一次請求產生獨立的 session
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
# FastAPI 用的依賴函式
async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session