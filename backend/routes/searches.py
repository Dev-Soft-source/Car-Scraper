from optparse import Option
from unicodedata import category
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from backend.database.config import get_db
from backend.models.models import User, Search
from backend.utils.dependencies import get_current_user
from backend.services.scraping_service import scraping_service
from backend.models.models import UserSettings
from datetime import datetime
from typing import Any
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix='/searches', tags=['Searches'])
scraper_status = {"running_loop": False}
class SearchCreate(BaseModel):
    name: str
    description: Optional[str] = None
    keyword: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    category: Optional[int] = None
    mileage_max: Optional[int] = None
    power: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    fuel_type: Optional[str] = None
    location: Optional[str] = None
    seller: Optional[str] = None
    site_url: Optional[str] = None
    target_price: Optional[float] = None
    is_active: Optional[bool] = True

class SearchUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    keyword: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    category: Optional[int] = None
    mileage_max: Optional[int] = None
    power: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    fuel_type: Optional[str] = None
    location: Optional[str] = None
    seller: Optional[str] = None
    target_price: Optional[float] = None
    site_url: Optional[str] = None
    is_active: Optional[bool] = None

class SearchResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    keyword: Optional[str]
    make: Optional[str]
    model: Optional[str]
    category: Optional[int]
    year_from: Optional[int]
    year_to: Optional[int]
    mileage_max: Optional[int]
    price_min: Optional[float]
    price_max: Optional[float]
    fuel_type: Optional[str]
    location: Optional[str]
    seller: Optional[str]
    target_price: Optional[float]
    is_active: bool
    is_favorite: bool
    site_url: Optional[str] = None
    created_at: datetime
    last_search_date: Optional[datetime]
    
    class Config:
        from_attributes = True

class ScraperStatsSchema(BaseModel):
    running: bool

@router.get('/state', response_model=ScraperStatsSchema)
def get_state(user: Any = Depends(get_current_user)):
    return ScraperStatsSchema(running=scraper_status["running_loop"])

@router.get('', response_model=List[SearchResponse])
def get_all_searches(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    searches = db.query(Search).filter(Search.user_id == current_user.id).all()
    return searches

@router.get('/{search_id}', response_model=SearchResponse)
def get_search(search_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    search = db.query(Search).filter(Search.id == search_id, Search.user_id == current_user.id).first()
    if not search:
        raise HTTPException(status_code=404, detail='Search not found')
    return search

@router.post('', response_model=SearchResponse, status_code=status.HTTP_201_CREATED)
def create_search(search_data: SearchCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_search = Search(
        user_id=current_user.id,
        **search_data.model_dump()
    )
    db.add(new_search)
    db.commit()
    db.refresh(new_search)
    return new_search

@router.put('/{search_id}', response_model=SearchResponse)
def update_search(search_id: str, search_data: SearchUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    search = db.query(Search).filter(Search.id == search_id, Search.user_id == current_user.id).first()
    if not search:
        raise HTTPException(status_code=404, detail='Search not found')
    
    update_data = search_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(search, key, value)
    
    db.commit()
    db.refresh(search)
    return search


@router.delete('/{search_id}')
def delete_search(search_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    search = db.query(Search).filter(Search.id == search_id, Search.user_id == current_user.id).first()
    if not search:
        raise HTTPException(status_code=404, detail='Search not found')
    
    # Stop scraping if active
    scraping_service.stop_search_scraping(search_id)
    
    db.delete(search)
    db.commit()
    return {'message': 'Search deleted successfully'}

@router.post('/{search_id}/start')
def start_search(search_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    search = db.query(Search).filter(Search.id == search_id, Search.user_id == current_user.id).first()
    if not search:
        raise HTTPException(status_code=404, detail='Search not found')
    # Get user settings for interval
    
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    interval = settings.scraping_interval if settings else 60

    scraper_status["running_loop"] = True
    success = scraping_service.start_search_scraping(search_id, current_user.id, interval)
    if success:
        return {'message': 'Scraping started', 'search_id': search_id}
    else:
        raise HTTPException(status_code=400, detail='Failed to start scraping')

@router.post('/{search_id}/stop')
def stop_search(search_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    scraper_status["running_loop"] = False
    search = db.query(Search).filter(Search.id == search_id, Search.user_id == current_user.id).first()
    if not search:
        raise HTTPException(status_code=404, detail='Search not found')
    
    success = scraping_service.stop_search_scraping(search_id)
    
    if success:
        return {'message': 'Scraping stopped', 'search_id': search_id}
    else:
        raise HTTPException(status_code=400, detail='Failed to stop scraping')

@router.post('/{search_id}/favorite')
def toggle_favorite(search_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    search = db.query(Search).filter(Search.id == search_id, Search.user_id == current_user.id).first()
    if not search:
        raise HTTPException(status_code=404, detail='Search not found')
    
    search.is_favorite = not search.is_favorite
    db.commit()
    return {'message': 'Favorite toggled', 'is_favorite': search.is_favorite}
