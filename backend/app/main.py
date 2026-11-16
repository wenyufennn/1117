# backend/app/main.py
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI(title="投稿審查系統")

# 靜態目錄路徑設定
www_path = Path(__file__).resolve().parent.parent.parent / "www"
if not www_path.exists():
    www_path = Path(__file__).resolve().parent / "static"

app.mount("/static", StaticFiles(directory=str(www_path)), name="static")

from .routes import manuscript, auth

# 掛載認證路由
app.include_router(auth.router)

# 掛載作者與編輯路由
app.include_router(manuscript.router)
app.include_router(manuscript.editor_router)

@app.get("/", include_in_schema=False)
def root():
    # 根路由自動導向頁面1 (登入頁面)
    return RedirectResponse(url="/static/index.html")
