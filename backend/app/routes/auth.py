import re
from fastapi import APIRouter, HTTPException, Depends, status, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from ..models import User
from ..deps import get_db
from ..security import verify_password, get_password_hash, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    username = credentials.username.strip()
    password = credentials.password.strip()

    # 特殊處理 host 帳號 (若資料庫中尚無 host，自動建立)
    if username == "host" and password == "123":
        host_user = db.query(User).filter(User.username == "host").first()
        if not host_user:
            host_user = User(
                username="host",
                password_hash=get_password_hash("123"),
                role="editor"
            )
            db.add(host_user)
            db.commit()
            db.refresh(host_user)
        token = create_access_token({"sub": "host", "role": "editor"})
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": "editor",
            "username": "host"
        }

    # 一般使用者驗證
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤"
        )

    token = create_access_token({"sub": user.username, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username
    }


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    username = data.username.strip()
    password = data.password.strip()

    if not re.match(r'^[a-zA-Z0-9]+$', username):
        raise HTTPException(status_code=400, detail="帳號僅限數字、英文或數字英文組合")
    if not re.match(r'^[a-zA-Z0-9]+$', password):
        raise HTTPException(status_code=400, detail="密碼僅限數字、英文或數字英文組合")

    if username.lower() == "host":
        raise HTTPException(status_code=400, detail="不可註冊 host 帳號")

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="該帳號已被使用，請選擇其他帳號")

    hashed = get_password_hash(password)
    new_user = User(
        username=username,
        password_hash=hashed,
        role="author"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.username, "role": new_user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": new_user.role,
        "username": new_user.username,
        "message": "註冊成功"
    }


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供身分驗證憑證，請先登入"
        )
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    username = payload.get("sub")
    role = payload.get("role")
    if not username or not role:
        raise HTTPException(status_code=401, detail="無效的憑證資訊")
    return {"username": username, "role": role}


def require_role(required_role: str):
    def checker(user: dict = Depends(get_current_user)):
        if user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"權限不足：需要 {required_role} 權限"
            )
        return user
    return checker
