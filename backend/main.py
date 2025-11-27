from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import database and models
from database.config import Base, engine
from models import models

# Import routes
from routes import auth, searches, listings, settings, logs

# Import scraping service
from services.scraping_service import scraping_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Start scraping service
    try:
        scraping_service.start()
        logger.info("Scraping service started")
    except Exception as e:
        logger.error(f"Error starting scraping service: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        scraping_service.stop()
        logger.info("Scraping service stopped")
    except Exception as e:
        logger.error(f"Error stopping scraping service: {e}")

# Create the main app
app = FastAPI(title="Wallapop Scraper API", lifespan=lifespan)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Test endpoint
@api_router.get("/")
async def root():
    return {"message": "Wallapop Scraper API", "status": "running"}

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(searches.router)
api_router.include_router(listings.router)
api_router.include_router(settings.router)
api_router.include_router(logs.router)

# Include the router in the main app
app.include_router(api_router)

origins = [
   "https://cars-scraperf.onrender.com",  # frontend ngrok URL
   # "http://localhost:3000",  # frontend ngrok URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or only your ngrok frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Application initialized successfully")