import re
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


def validate_username_password(val: str, field_name: str) -> str:
    if not re.match(r'^[a-zA-Z0-9]+$', val):
        raise ValueError(f"{field_name}僅限數字、英文或數字英文組合")
    return val


# ---------- Users ----------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "author"

    @field_validator("username")
    @classmethod
    def check_username(cls, v: str) -> str:
        return validate_username_password(v, "帳號")

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return validate_username_password(v, "密碼")


class UserRead(BaseModel):
    id: int
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)


# ---------- Manuscripts ----------
class ManuscriptBase(BaseModel):
    category: str
    title: str
    content: str


class ManuscriptCreate(ManuscriptBase):
    @field_validator("content")
    @classmethod
    def check_content(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("文章內容不可為空")
        return v


class ManuscriptUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None

    @field_validator("content")
    @classmethod
    def check_content(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("文章內容不可為空")
        return v


class ManuscriptRead(BaseModel):
    id: int
    author_id: int
    author_name: Optional[str] = None
    category: str
    title: str
    content: str
    status: str
    status_display: Optional[str] = None
    reject_notice: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
