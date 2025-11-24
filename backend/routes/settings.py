from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database.config import get_db
from models.models import User, UserSettings, SiteUrl
from utils.dependencies import get_current_user
from utils.auth import verify_password, get_password_hash
from datetime import datetime

router = APIRouter(prefix='/settings', tags=['Settings'])

class SettingsResponse(BaseModel):
    scraping_interval: int
    keyword: Optional[str]
    category: Optional[str]
    price_range_min: float
    price_range_max: float
    target_price: float
    
    class Config:
        from_attributes = True

class SettingsUpdate(BaseModel):
    scraping_interval: Optional[int] = None
    keyword: Optional[str] = None
    category: Optional[str] = None
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    target_price: Optional[float] = None

class SiteUrlCreate(BaseModel):
    url: str

class SiteUrlResponse(BaseModel):
    id: str
    url: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.get('', response_model=SettingsResponse)
def get_settings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        # Create default settings
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put('', response_model=SettingsResponse)
def update_settings(
    settings_data: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    update_data = settings_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(settings, key, value)
    
    db.commit()
    db.refresh(settings)
    return settings

@router.post('/change-password')
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify old password
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Incorrect old password'
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return {'message': 'Password changed successfully'}

@router.get('/site-urls', response_model=List[SiteUrlResponse])
def get_site_urls(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    urls = db.query(SiteUrl).filter(SiteUrl.user_id == current_user.id).all()
    return urls

@router.post('/site-urls', response_model=SiteUrlResponse, status_code=status.HTTP_201_CREATED)
def add_site_url(
    url_data: SiteUrlCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_url = SiteUrl(
        user_id=current_user.id,
        url=url_data.url
    )
    print("sdlkfsdlfksdljfklsdj: ", url_data.url)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return new_url

@router.delete('/site-urls/{url_id}')
def delete_site_url(
    url_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    url = db.query(SiteUrl).filter(SiteUrl.id == url_id, SiteUrl.user_id == current_user.id).first()
    if not url:
        raise HTTPException(status_code=404, detail='URL not found')
    
    db.delete(url)
    db.commit()
    return {'message': 'URL deleted successfully'}
