from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database.config import get_db
from models.models import User, Listing, Search
from utils.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix='/listings', tags=['Listings'])

class ListingResponse(BaseModel):
    id: str
    search_id: str
    platform_id: str
    title: Optional[str]
    description: Optional[str]
    make: Optional[str]
    model: Optional[str]
    year: Optional[int]
    mileage: Optional[int]
    price: Optional[float]
    fuel_type: Optional[str]
    location: Optional[str]
    seller_type: Optional[str]
    average_price: Optional[float]
    target_price_met: bool
    is_favorite: bool
    platform_url: Optional[str]
    image_url: Optional[str]
    last_updated: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get('', response_model=List[ListingResponse])
def get_all_listings(
    make: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    location: Optional[str] = Query(None),
    seller_type: Optional[str] = Query(None),
    target_price_only: Optional[bool] = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get all searches for the user
    user_searches = db.query(Search).filter(Search.user_id == current_user.id).all()
    search_ids = [s.id for s in user_searches]
    
    query = db.query(Listing).filter(Listing.search_id.in_(search_ids))
    
    # Apply filters
    if make:
        query = query.filter(Listing.make.ilike(f'%{make}%'))
    if model:
        query = query.filter(Listing.model.ilike(f'%{model}%'))
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    if location:
        query = query.filter(Listing.location.ilike(f'%{location}%'))
    if seller_type:
        query = query.filter(Listing.seller_type == seller_type)
    if target_price_only:
        query = query.filter(Listing.target_price_met == True)
    
    listings = query.order_by(Listing.last_updated.desc()).all()
    return listings

@router.get('/search/{search_id}', response_model=List[ListingResponse])
def get_listings_by_search(
    search_id: str,
    make: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    location: Optional[str] = Query(None),
    seller_type: Optional[str] = Query(None),
    target_price_only: Optional[bool] = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify search belongs to user
    search = db.query(Search).filter(Search.id == search_id, Search.user_id == current_user.id).first()
    if not search:
        raise HTTPException(status_code=404, detail='Search not found')
    
    query = db.query(Listing).filter(Listing.search_id == search_id)
    
    # Apply filters
    if make:
        query = query.filter(Listing.make.ilike(f'%{make}%'))
    if model:
        query = query.filter(Listing.model.ilike(f'%{model}%'))
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    if location:
        query = query.filter(Listing.location.ilike(f'%{location}%'))
    if seller_type:
        query = query.filter(Listing.seller_type == seller_type)
    if target_price_only:
        query = query.filter(Listing.target_price_met == True)
    
    listings = query.order_by(Listing.last_updated.desc()).all()
    return listings

@router.get('/{listing_id}', response_model=ListingResponse)
def get_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail='Listing not found')
    
    # Verify listing belongs to user's search
    search = db.query(Search).filter(Search.id == listing.search_id, Search.user_id == current_user.id).first()
    if not search:
        raise HTTPException(status_code=403, detail='Access denied')
    
    return listing

@router.post('/{listing_id}/favorite')
def toggle_favorite(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail='Listing not found')
    
    # Verify listing belongs to user's search
    search = db.query(Search).filter(Search.id == listing.search_id, Search.user_id == current_user.id).first()
    if not search:
        raise HTTPException(status_code=403, detail='Access denied')
    
    listing.is_favorite = not listing.is_favorite
    db.commit()
    return {'message': 'Favorite toggled', 'is_favorite': listing.is_favorite}

@router.get('/statistics/overview')
def get_statistics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from models.models import Statistics
    from sqlalchemy import func
    
    # Get user's searches
    user_searches = db.query(Search).filter(Search.user_id == current_user.id).all()
    search_ids = [s.id for s in user_searches]
    
    # Get statistics
    total_listings = db.query(Listing).filter(Listing.search_id.in_(search_ids)).count()
    below_target = db.query(Listing).filter(
        Listing.search_id.in_(search_ids),
        Listing.target_price_met == True
    ).count()
    favorites = db.query(Listing).filter(
        Listing.search_id.in_(search_ids),
        Listing.is_favorite == True
    ).count()
    
    avg_price = db.query(func.avg(Listing.price)).filter(
        Listing.search_id.in_(search_ids),
        Listing.price > 0
    ).scalar() or 0
    
    return {
        'total_listings': total_listings,
        'below_target': below_target,
        'favorites': favorites,
        'average_price': float(avg_price)
    }
