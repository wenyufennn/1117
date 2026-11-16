from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import SQLALCHEMY_DATABASE_URL

# Declarative base for ORM models
Base = declarative_base()

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
