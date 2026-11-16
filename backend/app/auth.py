from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt, os
from ..models import User
from ..deps import get_db
from ..schemas.user import UserCreate, UserRead
router = APIRouter()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
JWT_SECRET = os.getenv('JWT_SECRET', 'change_me')
@router.post('/register', response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail='Email already registered')
    hashed = pwd_context.hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
@router.post('/login')
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    token = jwt.encode({'sub': db_user.id}, JWT_SECRET, algorithm='HS256')
    return {'access_token': token}
