from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import Manuscript
from ..deps import get_db
from ..schemas.manuscript import ManuscriptCreate, ManuscriptRead
router = APIRouter(prefix='/manuscripts')
@router.post('/', response_model=ManuscriptRead)
def create(ms: ManuscriptCreate, db: Session = Depends(get_db)):
    db_ms = Manuscript(**ms.dict())
    db.add(db_ms)
    db.commit()
    db.refresh(db_ms)
    return db_ms
@router.get('/{ms_id}', response_model=ManuscriptRead)
def read(ms_id: int, db: Session = Depends(get_db)):
    ms = db.query(Manuscript).filter(Manuscript.id == ms_id).first()
    if not ms:
        raise HTTPException(status_code=404, detail='Not found')
    return ms
@router.patch('/{ms_id}/submit')
def submit(ms_id: int, db: Session = Depends(get_db)):
    ms = db.query(Manuscript).filter(Manuscript.id == ms_id).first()
    if not ms:
        raise HTTPException(status_code=404, detail='Not found')
    ms.status = 'submitted'
    db.commit()
    return {'msg': 'submitted'}
