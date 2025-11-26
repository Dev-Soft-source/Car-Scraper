from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from database.config import SessionLocal
from models.models import Search, Listing, Log, Statistics, UserSettings
from scrapers.wallapop_scraper import WallapopScraper
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

class ScrapingService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.active_jobs = {}  # search_id -> job_id mapping
        self.scrapers = {}  # search_id -> scraper instance
        
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scraping scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scraping scheduler stopped")
    
    def start_search_scraping(self, search_id: str, user_id: str, interval_minutes: int = 60):
        """Start periodic scraping for a search"""
        if search_id in self.active_jobs:
            logger.warning(f"Scraping already active for search {search_id}")
            return False
        
        try:
            # Add job to scheduler
            job = self.scheduler.add_job(
                func=self._scrape_search,
                trigger=IntervalTrigger(minutes=interval_minutes),
                args=[search_id, user_id],
                id=f"scrape_{search_id}",
                replace_existing=True
            )
            
            self.active_jobs[search_id] = job.id
            
            # Run immediately
            self._scrape_search(search_id, user_id)
            
            logger.info(f"Started scraping for search {search_id} with {interval_minutes} minute interval")
            return True
            
        except Exception as e:
            logger.error(f"Error starting scraping for search {search_id}: {e}")
            return False
    
    def stop_search_scraping(self, search_id: str):
        """Stop scraping for a search"""
        if search_id not in self.active_jobs:
            logger.warning(f"No active scraping for search {search_id}")
            return False
        
        try:
            job_id = self.active_jobs[search_id]
            self.scheduler.remove_job(job_id)
            del self.active_jobs[search_id]
            
            # Close scraper if exists
            if search_id in self.scrapers:
                self.scrapers[search_id].close()
                del self.scrapers[search_id]
            
            logger.info(f"Stopped scraping for search {search_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping scraping for search {search_id}: {e}")
            return False
    
    def _scrape_search(self, search_id: str, user_id: str):
        """Perform scraping for a specific search"""
        db = SessionLocal()
        
        try:
            # Get search criteria
            search = db.query(Search).filter(Search.id == search_id, Search.user_id == user_id).first()
            if search is None or not bool(search.is_active):
                logger.warning(f"Search {search_id} not found or inactive")
                return

            print("Search: ", search)
            
            # Log start
            log = Log(
                level='info',
                message=f"Starting scrape for search: {search.name}",
                search_name=search.name
            )
            db.add(log)
            db.commit()

            # Initialize scraper
            if search_id not in self.scrapers:
                self.scrapers[search_id] = WallapopScraper(headless=False)
            
            scraper = self.scrapers[search_id]
            
            # Prepare search criteria
            search_criteria = {
                'make': search.make,
                'model': search.model,
                'price_min': search.price_min,
                'price_max': search.price_max,
                'power': search.power,
                'keyword': search.keyword,
                'mileage_max': search.mileage_max,
                'location': search.location,
                'fuel_type': search.fuel_type,
                'site_url': search.site_url,
                'name': search.name,
                'category': search.category,
                'target_price': search.target_price,
                'seller': search.seller,
                'year_from': search.year_from,
                'year_to': search.year_to,
                'last_search_date': search.last_search_date
            }
            
            # Perform scraping
            logger.info(f"Scraping with criteria: {search_criteria}")
            scraped_listings = scraper.scrape_listings(search_criteria)
            
            # Process listings
            new_count = 0
            updated_count = 0
            below_target_count = 0

            for listing_data in scraped_listings:
                try:
                    # Check if listing exists
                    existing = db.query(Listing).filter(
                        Listing.platform_id == listing_data.get('platform_id')
                    ).first()
                    
                    # Calculate if below target
                    target_met = False
                    target_price = getattr(search, 'target_price', None)
                    price = listing_data.get('price')
                    # Ensure both target_price and price are present and are numbers
                    if target_price is not None and price is not None:
                        try:
                            # Convert to float if possible (handles Decimal, str, int)
                            tp = float(target_price)
                            p = float(price)
                            target_met = p <= tp
                        except (TypeError, ValueError):
                            target_met = False
                        if target_met:
                            below_target_count += 1
                    if existing:
                        # Update existing listing
                        existing.price = listing_data.get('price', existing.price)
                        existing.title = listing_data.get('title', existing.title)
                        existing.description = listing_data.get('description', existing.description)
                        existing.location = listing_data.get('location', existing.location)
                        existing.target_price_met = target_met
                        existing.last_updated = datetime.utcnow()
                        updated_count += 1
                    else:
                        # Create new listing
                        new_listing = Listing(
                            search_id=search_id,
                            platform_id=listing_data.get('platform_id'),
                            title=listing_data.get('title'),
                            description=listing_data.get('description'),
                            make=listing_data.get('make'),
                            model=listing_data.get('model'),
                            year=listing_data.get('year'),
                            mileage=listing_data.get('mileage'),
                            price=listing_data.get('price'),
                            fuel_type=listing_data.get('fuel_type'),
                            location=listing_data.get('location'),
                            seller_type=listing_data.get('seller_type', 'Private'),
                            target_price_met=target_met,
                            platform_url=listing_data.get('platform_url'),
                            image_url=listing_data.get('image_url')
                        )
                        db.add(new_listing)
                        new_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing listing: {e}")
                    continue
            
            # Calculate average price
            
            all_listings = db.query(Listing).filter(Listing.search_id == search_id).all()
            # Gather all prices, ensuring valid prices are converted to float
            prices = []
            for l in all_listings:
                try:
                    # Ensure l.price is a valid number (either int or float)
                    price = float(l.price)  # Convert to float
                    if price > 0:
                        prices.append(price)
                except (ValueError, TypeError) as e:
                    logger.error(f"Invalid price value '{l.price}' for listing {l.id}: {e}")
                    continue  # Skip invalid price

            # If we have valid prices, calculate the average
            if prices:
                avg_price = sum(prices) / len(prices)
                
                # Update average price for all listings
                for listing in all_listings:
                    listing.average_price = avg_price

                # Save statistics
                stat = Statistics(
                    date=datetime.utcnow(),
                    make=search.make,
                    model=search.model,
                    average_price=avg_price,
                    count=len(prices)
                )
                db.add(stat)
            # Update search last_search_date
            search.last_search_date = datetime.utcnow()
            
            db.commit()
            
            # Log success
            success_log = Log(
                level='success',
                message=f"Scraping completed for {search.name}",
                search_name=search.name,
                details=json.dumps({
                    'new_listings': new_count,
                    'updated_listings': updated_count,
                    'below_target': below_target_count,
                    'total_scraped': len(scraped_listings)
                })
            )
            db.add(success_log)
            db.commit()
            
            logger.info(f"Scraping completed: {new_count} new, {updated_count} updated, {below_target_count} below target")
            
        except Exception as e:
            logger.error(f"Error in scraping: {e}")
            
            # Log error
            error_log = Log(
                level='error',
                message=f"Scraping failed: {str(e)}",
                search_name=search.name if search else 'Unknown',
                details=str(e)
            )
            db.add(error_log)
            db.commit()
            
        finally:
            db.close()

# Global instance
scraping_service = ScrapingService()
