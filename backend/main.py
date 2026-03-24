from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# Load env
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

from database.config import Base, engine
from models import models
from routes import auth, searches, listings, settings, logs
from services.scraping_service import scraping_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    Base.metadata.create_all(bind=engine)
    scraping_service.start()
    yield
    logger.info("Shutting down application...")
    scraping_service.stop()

app = FastAPI(title="Wallapop Scraper API", lifespan=lifespan)

origins = [
   # "https://cars-scraperf.onrender.com",  # frontend ngrok URL
   "http://localhost:3000"  # frontend ngrok URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or only your ngrok frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def root():
    return {"message": "Wallapop Scraper API", "status": "running"}

api_router.include_router(auth.router)
api_router.include_router(searches.router)
api_router.include_router(listings.router)
api_router.include_router(settings.router)
api_router.include_router(logs.router)

app.include_router(api_router)
logger.info("Application initialized successfully")