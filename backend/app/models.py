from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(10), default="author", nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    manuscripts = relationship("Manuscript", back_populates="author", cascade="all, delete-orphan")


class Manuscript(Base):
    __tablename__ = "manuscripts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(30), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(10), default="draft", nullable=False)  # 'draft', 'review', 'approved'
    reject_notice = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    author = relationship("User", back_populates="manuscripts")
