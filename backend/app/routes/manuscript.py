import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models, schemas
from ..deps import get_db
from .auth import get_current_user, require_role

router = APIRouter(prefix="/author", tags=["author"])
editor_router = APIRouter(prefix="/editor", tags=["editor"])

STATUS_MAP_TO_DISPLAY = {
    "draft": "編輯中",
    "review": "審查中",
    "approved": "已通過"
}


def validate_content(content: str):
    if not content or not content.strip():
        raise HTTPException(status_code=400, detail="文章內容不可為空")


def to_manuscript_read(ms: models.Manuscript) -> dict:
    return {
        "id": ms.id,
        "author_id": ms.author_id,
        "author_name": ms.author.username if ms.author else "",
        "category": ms.category,
        "title": ms.title,
        "content": ms.content,
        "status": ms.status,
        "status_display": STATUS_MAP_TO_DISPLAY.get(ms.status, ms.status),
        "reject_notice": ms.reject_notice,
        "created_at": ms.created_at,
        "updated_at": ms.updated_at
    }


# ==========================================
# 作者功能 API (頁面2及子頁面)
# ==========================================

@router.get("/articles", dependencies=[Depends(require_role("author"))])
def list_author_articles(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.username == current_user["username"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="找不到使用者")
    
    manuscripts = db.query(models.Manuscript).filter(models.Manuscript.author_id == user.id).order_by(models.Manuscript.id.desc()).all()
    return [to_manuscript_read(m) for m in manuscripts]


@router.get("/articles/{mid}", dependencies=[Depends(require_role("author"))])
def get_author_article(mid: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.username == current_user["username"]).first()
    ms = db.query(models.Manuscript).filter(models.Manuscript.id == mid, models.Manuscript.author_id == user.id).first()
    if not ms:
        raise HTTPException(status_code=404, detail="找不到該稿件")
    return to_manuscript_read(ms)


@router.post("/articles", dependencies=[Depends(require_role("author"))])
def create_manuscript(ms: schemas.ManuscriptCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    validate_content(ms.content)
    user = db.query(models.User).filter(models.User.username == current_user["username"]).first()
    
    manuscript = models.Manuscript(
        author_id=user.id,
        category=ms.category.strip(),
        title=ms.title.strip(),
        content=ms.content.strip(),
        status="draft",
        reject_notice=None
    )
    db.add(manuscript)
    db.commit()
    db.refresh(manuscript)
    return to_manuscript_read(manuscript)


@router.put("/articles/{mid}", dependencies=[Depends(require_role("author"))])
def edit_manuscript(mid: int, ms: schemas.ManuscriptUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.username == current_user["username"]).first()
    manuscript = db.query(models.Manuscript).filter(models.Manuscript.id == mid, models.Manuscript.author_id == user.id).first()
    if not manuscript:
        raise HTTPException(status_code=404, detail="找不到該稿件")
    if manuscript.status != "draft":
        raise HTTPException(status_code=400, detail="只有狀態為「編輯中」的稿件才可編輯")
    
    if ms.category is not None:
        manuscript.category = ms.category.strip()
    if ms.title is not None:
        manuscript.title = ms.title.strip()
    if ms.content is not None:
        validate_content(ms.content)
        manuscript.content = ms.content.strip()
        
    db.commit()
    db.refresh(manuscript)
    return to_manuscript_read(manuscript)


@router.delete("/articles/{mid}", dependencies=[Depends(require_role("author"))])
def delete_manuscript(mid: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.username == current_user["username"]).first()
    manuscript = db.query(models.Manuscript).filter(models.Manuscript.id == mid, models.Manuscript.author_id == user.id).first()
    if not manuscript:
        raise HTTPException(status_code=404, detail="找不到該稿件")
    if manuscript.status != "draft":
        raise HTTPException(status_code=400, detail="只有狀態為「編輯中」的稿件才可刪除")
    
    db.delete(manuscript)
    db.commit()
    return {"message": "稿件已成功刪除"}


@router.post("/articles/{mid}/submit", dependencies=[Depends(require_role("author"))])
def submit_manuscript(mid: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.username == current_user["username"]).first()
    manuscript = db.query(models.Manuscript).filter(models.Manuscript.id == mid, models.Manuscript.author_id == user.id).first()
    if not manuscript:
        raise HTTPException(status_code=404, detail="找不到該稿件")
    if manuscript.status != "draft":
        raise HTTPException(status_code=400, detail="只有狀態為「編輯中」的稿件才可送出投稿")
    
    manuscript.status = "review"
    manuscript.reject_notice = None  # 送出後清除退回標記
    db.commit()
    db.refresh(manuscript)
    return to_manuscript_read(manuscript)


# ==========================================
# 編輯審查功能 API (頁面3及子頁面)
# ==========================================

@editor_router.get("/review-queue", dependencies=[Depends(require_role("editor"))])
def get_review_queue(db: Session = Depends(get_db)):
    manuscripts = db.query(models.Manuscript).filter(models.Manuscript.status == "review").order_by(models.Manuscript.id.desc()).all()
    return [to_manuscript_read(m) for m in manuscripts]


@editor_router.get("/articles/{mid}", dependencies=[Depends(require_role("editor"))])
def get_editor_article(mid: int, db: Session = Depends(get_db)):
    manuscript = db.query(models.Manuscript).filter(models.Manuscript.id == mid).first()
    if not manuscript:
        raise HTTPException(status_code=404, detail="找不到該稿件")
    return to_manuscript_read(manuscript)


@editor_router.post("/articles/{mid}/approve", dependencies=[Depends(require_role("editor"))])
def approve_manuscript(mid: int, db: Session = Depends(get_db)):
    manuscript = db.query(models.Manuscript).filter(models.Manuscript.id == mid).first()
    if not manuscript or manuscript.status != "review":
        raise HTTPException(status_code=400, detail="只有「審查中」的稿件才能進行通過操作")
    
    manuscript.status = "approved"
    manuscript.reject_notice = None
    db.commit()
    db.refresh(manuscript)
    return to_manuscript_read(manuscript)


@editor_router.post("/articles/{mid}/reject", dependencies=[Depends(require_role("editor"))])
def reject_manuscript(mid: int, db: Session = Depends(get_db)):
    manuscript = db.query(models.Manuscript).filter(models.Manuscript.id == mid).first()
    if not manuscript or manuscript.status != "review":
        raise HTTPException(status_code=400, detail="只有「審查中」的稿件才能進行退回操作")
    
    manuscript.status = "draft"
    manuscript.reject_notice = "您的稿件已被審查員退回修改，請更新後重新送審。"
    db.commit()
    db.refresh(manuscript)
    return to_manuscript_read(manuscript)
