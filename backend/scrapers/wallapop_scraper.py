from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class WallapopScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        
    def _init_driver(self):
        """Initialize Chrome WebDriver with options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def _human_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """Add random delay to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def scrape_listings(self, search_criteria: Dict) -> List[Dict]:
        """
        Scrape Wallapop listings based on search criteria
        
        Args:
            search_criteria: Dict with keys: make, model, price_max, location, etc.
        
        Returns:
            List of listing dictionaries
        """
        if self.driver is None:
            self._init_driver()
        
        listings = []
        
        try:
            # Build search URL
            base_url = "https://es.wallapop.com/"
            
            # Add search parameters
            params = []
            if search_criteria.get('make'):
                params.append(f"keywords={search_criteria['make']}")
            if search_criteria.get('model'):
                params.append(f"{search_criteria['model']}")
            if search_criteria.get('price_max'):
                params.append(f"max_sale_price={search_criteria['price_max']}")
            if search_criteria.get('location'):
                params.append(f"latitude={search_criteria.get('latitude', 40.4168)}")
                params.append(f"longitude={search_criteria.get('longitude', -3.7038)}")
            
            search_url = f"{base_url}" #?{'&'.join(params)}"
            
            logger.info(f"Navigating to: {search_url}")
            self.driver.get(search_url)
            self._human_delay(2, 4)
            
            # Wait for listings to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ItemCardList__item"))
                )
            except Exception as e:
                logger.warning(f"No listings found or timeout: {e}")
                return listings
            
            # Scroll to load more items
            self._scroll_page()
            
            # Extract listings
            listing_elements = self.driver.find_elements(By.CLASS_NAME, "ItemCardList__item")
            logger.info(f"Found {len(listing_elements)} listing elements")
            
            for idx, element in enumerate(listing_elements[:20]):  # Limit to 20 listings per scrape
                try:
                    listing_data = self._extract_listing_data(element, idx)
                    if listing_data:
                        listings.append(listing_data)
                    self._human_delay(0.5, 1.5)
                except Exception as e:
                    logger.error(f"Error extracting listing {idx}: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(listings)} listings")
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
        
        return listings
    
    def _scroll_page(self):
        """Scroll page to load more content"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            for _ in range(3):  # Scroll 3 times
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self._human_delay(1, 2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            logger.warning(f"Error scrolling page: {e}")
    
    def _extract_listing_data(self, element, index: int) -> Optional[Dict]:
        """Extract data from a single listing element"""
        try:
            listing = {}
            
            # Extract title
            try:
                title_elem = element.find_element(By.CLASS_NAME, "ItemCard__title")
                listing['title'] = title_elem.text.strip()
            except:
                listing['title'] = f"Listing {index + 1}"
            
            # Extract price
            try:
                price_elem = element.find_element(By.CLASS_NAME, "ItemCard__price")
                price_text = price_elem.text.strip().replace('€', '').replace('.', '').replace(',', '.')
                listing['price'] = float(price_text)
            except:
                listing['price'] = 0.0
            
            # Extract description
            try:
                desc_elem = element.find_element(By.CLASS_NAME, "ItemCard__description")
                listing['description'] = desc_elem.text.strip()
            except:
                listing['description'] = ''
            
            # Extract location
            try:
                location_elem = element.find_element(By.CLASS_NAME, "ItemCard__location")
                listing['location'] = location_elem.text.strip()
            except:
                listing['location'] = ''
            
            # Extract URL
            try:
                link_elem = element.find_element(By.TAG_NAME, "a")
                listing['platform_url'] = link_elem.get_attribute('href')
                # Extract platform ID from URL
                if listing['platform_url']:
                    listing['platform_id'] = listing['platform_url'].split('/')[-1]
            except:
                listing['platform_url'] = ''
                listing['platform_id'] = f"listing_{index}_{int(time.time())}"
            
            # Extract image
            try:
                img_elem = element.find_element(By.TAG_NAME, "img")
                listing['image_url'] = img_elem.get_attribute('src')
            except:
                listing['image_url'] = ''
            
            # Try to extract vehicle details from title/description
            combined_text = f"{listing.get('title', '')} {listing.get('description', '')}".lower()
            
            # Extract year (look for 4-digit numbers between 1990-2025)
            import re
            year_match = re.search(r'\b(19[9][0-9]|20[0-2][0-9])\b', combined_text)
            if year_match:
                listing['year'] = int(year_match.group(1))
            
            # Extract mileage (look for km pattern)
            mileage_match = re.search(r'(\d{1,3}(?:\.\d{3})*)\s*km', combined_text)
            if mileage_match:
                mileage_str = mileage_match.group(1).replace('.', '')
                listing['mileage'] = int(mileage_str)
            
            # Determine seller type (if professional listing)
            listing['seller_type'] = 'Professional' if 'pro' in combined_text or 'profesional' in combined_text else 'Private'
            
            logger.debug(f"Extracted listing: {listing.get('title', 'Unknown')}")
            return listing
            
        except Exception as e:
            logger.error(f"Error in _extract_listing_data: {e}")
            return None
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()
