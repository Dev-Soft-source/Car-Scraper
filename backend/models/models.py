import keyword
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from backend.database.config import Base
from datetime import datetime
import enum
import uuid

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    searches = relationship('Search', back_populates='user', cascade='all, delete-orphan')
    settings = relationship('UserSettings', back_populates='user', uselist=False, cascade='all, delete-orphan')

class Search(Base):
    __tablename__ = 'searches'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    keyword = Column(String)
    interval = Column(Integer)
    make = Column(String)
    model = Column(String)
    year_from = Column(Integer)
    year_to = Column(Integer)
    category = Column(Integer)
    mileage_max = Column(Integer)
    price_min = Column(Float)
    price_max = Column(Float)
    fuel_type = Column(String)
    power = Column(String)
    location = Column(String)
    seller = Column(String)  # Private, Professional
    site_url = Column(String)
    target_price = Column(Float)
    is_active = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_search_date = Column(DateTime)
    
    user = relationship('User', back_populates='searches')
    listings = relationship('Listing', back_populates='search', cascade='all, delete-orphan')

class Listing(Base):
    __tablename__ = 'listings'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    search_id = Column(String, ForeignKey('searches.id'), nullable=False)
    platform_id = Column(String, unique=True)  # External ID from Wallapop
    title = Column(String)
    description = Column(Text)
    keyword = Column(String)
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    mileage = Column(Integer)
    price = Column(Float)
    power = Column(Integer)
    fuel_type = Column(String)
    location = Column(String)
    seller_type = Column(String)  # Private, Professional
    seller = Column(String) 
    average_price = Column(Float)
    target_price_met = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    platform_url = Column(String)
    image_url = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    search = relationship('Search', back_populates='listings')

class Statistics(Base):
    __tablename__ = 'statistics'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(DateTime, default=datetime.utcnow)
    make = Column(String)
    model = Column(String)
    average_price = Column(Float)
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class LogLevelEnum(enum.Enum):
    INFO = 'info'
    SUCCESS = 'success'
    WARNING = 'warning'
    ERROR = 'error'

class Log(Base):
    __tablename__ = 'logs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    level = Column(String, default='info')
    message = Column(Text, nullable=False)
    search_name = Column(String)
    details = Column(Text)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow)

class UserSettings(Base):
    __tablename__ = 'user_settings'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), unique=True, nullable=False)
    scraping_interval = Column(Integer, default=60)  # minutes
    keyword = Column(String)
    category = Column(String)
    price_range_min = Column(Float, default=0)
    price_range_max = Column(Float, default=50000)
    target_price = Column(Float, default=10000)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship('User', back_populates='settings')

class SiteUrl(Base):
    __tablename__ = 'site_urls'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
