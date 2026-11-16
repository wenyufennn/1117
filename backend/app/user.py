from pydantic import BaseModel, EmailStr
class UserCreate(BaseModel):
    email: EmailStr
    password: str
class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_editor: bool
    class Config:
        orm_mode = True
