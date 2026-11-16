from pydantic import BaseModel, ConfigDict
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
    # Pydantic v2 uses ConfigDict for ORM mode
    model_config = ConfigDict(from_attributes=True)

# Alias used by routes
class ManuscriptRead(ManuscriptOut):
    pass
