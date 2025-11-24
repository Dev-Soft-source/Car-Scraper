from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database.config import get_db
from models.models import User, Log
from utils.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix='/logs', tags=['Logs'])

class LogResponse(BaseModel):
    id: str
    level: str
    message: str
    search_name: Optional[str]
    details: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

@router.get('', response_model=List[LogResponse])
def get_logs(
    level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Log)
    
    # Apply filters
    if level:
        query = query.filter(Log.level == level.lower())
    if search:
        query = query.filter(Log.message.ilike(f'%{search}%'))
    
    logs = query.order_by(Log.timestamp.desc()).limit(limit).all()
    return logs

@router.get('/{log_id}', response_model=LogResponse)
def get_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = db.query(Log).filter(Log.id == log_id).first()
    if not log:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail='Log not found')
    return log
