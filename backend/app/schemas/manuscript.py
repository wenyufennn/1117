from pydantic import BaseModel
from typing import Optional

class ManuscriptBase(BaseModel):
    category: str
    title: str
    content: str

class ManuscriptCreate(ManuscriptBase):
    pass

class ManuscriptUpdate(BaseModel):
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None

class ManuscriptOut(ManuscriptBase):
    id: int
    status: str
    author_id: int

    class Config:
        orm_mode = True
