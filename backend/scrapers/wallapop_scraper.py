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

categories = {
    "Coches": "coches-segunda-mano",
    "Motos": "motos",
    "Inmobiliaria": "inmobiliaria",
    "Tecnología y electrónica": "tv-audio-foto",
    "Móviles y Telefonía": "moviles-telefonos",
    "Informática": "electronica",
    "Consolas y Videojuegos": "consolas-y-videojuegos",
    "Otros": "otros"
}

class WallapopScraper:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.driver = None
        
    def _init_driver(self):
        """Initialize Chrome WebDriver with options"""
        chrome_options = Options()
        
        # Basic options
        if self.headless:
            chrome_options.add_argument('--headless')  # Use new headless mode

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Better user agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Additional options for better compatibility
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--disable-site-isolation-trials')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        
        # Exclude automation flags
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set preferences
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 1
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to hide webdriver property
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def _human_delay(self, min_seconds: float = 1, max_seconds: float = 3):
        """Add random delay to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _handle_cookie_consent(self):
        """Handle cookie consent dialogs if they appear"""
        if not self.driver:
            return False
        try:
            # Wait a bit for cookie dialog to appear
            time.sleep(2)
            
            # Common selectors for cookie consent buttons
            cookie_selectors = [
                "button[id*='accept']",
                "button[class*='accept']",
                "button[class*='cookie']",
                "button[id*='cookie']",
                ".cookie-consent button",
                "#cookie-consent button",
                "button:contains('Aceptar')",
                "button:contains('Aceptar todas')",
                "button:contains('Accept')",
            ]
            
            for selector in cookie_selectors:
                try:
                    if not self.driver:
                        break
                    if 'contains' in selector:
                        # Use XPath for text-based matching
                        accept_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Aceptar') or contains(text(), 'Accept')]")
                    else:
                        accept_button = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    if accept_button:
                        accept_button.click()
                        logger.info("Cookie consent dialog handled")
                        self._human_delay(1, 2)
                        return True
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"No cookie consent dialog found or already handled: {e}")
        
        return False
    
    def _build_search_url(self, base_url: str, search_criteria: Dict) -> str:
        """Build Wallapop search URL from criteria"""
        params = []
        
        # Build keywords
        keywords = []
        if search_criteria.get('make'):
            keywords.append(search_criteria['make'])
        if search_criteria.get('model'):
            keywords.append(search_criteria['model'])
        
        if keywords:
            params.append(f"keywords={'%20'.join(keywords)}")
        
        # Price filter
        if search_criteria.get('price_max'):
            params.append(f"maxPrice={int(search_criteria['price_max'])}")
        
        # Location (default to Madrid if not specified)
        if search_criteria.get('location'):
            params.append(f"latitude={search_criteria.get('latitude', 40.4168)}")
            params.append(f"longitude={search_criteria.get('longitude', -3.7038)}")
        
        if params:
            return f"{base_url}/?{'&'.join(params)}"
        return "https://es.wallapop.com/"
    
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
            search_url = "https://es.wallapop.com/"
            logger.info(f"Navigating to: {search_url}")
            
            # Navigate to the page
            if not self.driver:
                raise Exception("WebDriver not initialized")
            self.driver.get(search_url)
            self._human_delay(3, 5)
            
            # Handle cookie consent
            self._handle_cookie_consent()
            
            # Wait for page to load - wait for main content
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                logger.info("Page loaded successfully")
            except Exception as e:
                logger.warning(f"Page load timeout, but continuing: {e}")
            
            # Additional wait for dynamic content
            self._human_delay(2, 4)

            # Try selecting the "Coches" category to focus on vehicle listings
            category_url = self._select_category(search_url, "Coches")

            search_url = self._build_search_url(category_url, search_criteria)

            print("Search_url: ", search_url)
            
            # Scroll to load more content
            self._scroll_page()
            
            # Find listing elements - try multiple selectors
            listing_selectors = [
                "article[class*='ItemCard']",
                "article[class*='item-card']",
                "article[class*='Card']",
                "div[class*='ItemCard']",
                "div[class*='item-card']",
                "a[class*='ItemCard']",
                "[data-testid='item-card']",
                ".item-card",
                "article",
            ]
            
            listing_elements = []
            for selector in listing_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and len(elements) > 0:
                        listing_elements = elements
                        logger.info(f"Found {len(elements)} listings using selector: {selector}")
                        break
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            if not listing_elements:
                logger.warning("No listing elements found. Trying alternative approach...")
                # Try to find any clickable items that might be listings
                listing_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/item/']")
                logger.info(f"Found {len(listing_elements)} potential listings via link href")
            
            # Extract data from each listing
            for index, element in enumerate(listing_elements[:50]):  # Limit to 50 listings
                try:
                    listing_data = self._extract_listing_data(element, index)
                    if listing_data and listing_data.get('title'):
                        listings.append(listing_data)
                except Exception as e:
                    logger.error(f"Error extracting listing {index}: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(listings)} listings")
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}", exc_info=True)
            raise
        
        return listings

    def _select_category(self, search_url: str, category_name: str) -> str:
        """Selects a Wallapop category using top navigation or the drawer (shadow DOM)."""
        if not self.driver:
            return search_url
        # ---------------------------------------------------
        # 3️⃣ PHASE 3: Try shadow DOM search
        # ---------------------------------------------------
        result = categories[category_name]
        if result:
            cate_url = search_url + result
            self._human_delay(1, 2)
            # >>> Navigate to the category URL
            try:
                self.driver.get(cate_url)
                return cate_url
            except Exception as e:
                print("Navigation Category_url failed:", e)
                return search_url
        else:
            return search_url
    
    def _scroll_page(self):
        """Scroll page to load more content"""
        if not self.driver:
            return
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
            import re
            
            # Try to get element text for fallback
            element_text = ""
            try:
                element_text = element.text
            except:
                pass
            
            # Extract title - try multiple selectors
            title_selectors = [
                (By.CLASS_NAME, "ItemCard__title"),
                (By.CSS_SELECTOR, "[class*='title']"),
                (By.CSS_SELECTOR, "h2"),
                (By.CSS_SELECTOR, "h3"),
                (By.TAG_NAME, "h2"),
                (By.TAG_NAME, "h3"),
            ]
            
            listing['title'] = f"Listing {index + 1}"
            for by, selector in title_selectors:
                try:
                    title_elem = element.find_element(by, selector)
                    if title_elem and title_elem.text.strip():
                        listing['title'] = title_elem.text.strip()
                        break
                except:
                    continue
            
            # If still no title, try getting from link text or aria-label
            if listing['title'] == f"Listing {index + 1}":
                try:
                    link = element.find_element(By.TAG_NAME, "a")
                    title_attr = link.get_attribute('aria-label') or link.get_attribute('title') or link.text.strip()
                    if title_attr:
                        listing['title'] = title_attr
                except:
                    pass
            
            # Extract price - try multiple selectors
            price_selectors = [
                (By.CLASS_NAME, "ItemCard__price"),
                (By.CSS_SELECTOR, "[class*='price']"),
                (By.CSS_SELECTOR, "[class*='Price']"),
                (By.CSS_SELECTOR, "span[class*='price']"),
            ]
            
            listing['price'] = 0.0
            for by, selector in price_selectors:
                try:
                    price_elem = element.find_element(by, selector)
                    price_text = price_elem.text.strip()
                    if price_text:
                        # Extract price number
                        price_match = re.search(r'[\d.,]+', price_text.replace('€', '').replace('EUR', ''))
                        if price_match:
                            price_str = price_match.group(0).replace('.', '').replace(',', '.')
                            listing['price'] = float(price_str)
                            break
                except:
                    continue
            
            # Extract description
            desc_selectors = [
                (By.CLASS_NAME, "ItemCard__description"),
                (By.CSS_SELECTOR, "[class*='description']"),
                (By.CSS_SELECTOR, "p"),
            ]
            
            listing['description'] = ''
            for by, selector in desc_selectors:
                try:
                    desc_elem = element.find_element(by, selector)
                    if desc_elem and desc_elem.text.strip():
                        listing['description'] = desc_elem.text.strip()
                        break
                except:
                    continue
            
            # Extract location
            location_selectors = [
                (By.CLASS_NAME, "ItemCard__location"),
                (By.CSS_SELECTOR, "[class*='location']"),
                (By.CSS_SELECTOR, "[class*='Location']"),
            ]
            
            listing['location'] = ''
            for by, selector in location_selectors:
                try:
                    location_elem = element.find_element(by, selector)
                    if location_elem and location_elem.text.strip():
                        listing['location'] = location_elem.text.strip()
                        break
                except:
                    continue
            
            # Extract URL - try multiple approaches
            listing['platform_url'] = ''
            listing['platform_id'] = f"listing_{index}_{int(time.time())}"
            
            try:
                # First try to find link in element
                link_elem = element.find_element(By.TAG_NAME, "a")
                href = link_elem.get_attribute('href')
                if href:
                    listing['platform_url'] = href if href.startswith('http') else f"https://es.wallapop.com{href}"
                    # Extract platform ID from URL
                    url_parts = listing['platform_url'].split('/')
                    for part in reversed(url_parts):
                        if part and part not in ['item', 'detail', '']:
                            listing['platform_id'] = part.split('?')[0]  # Remove query params
                            break
            except:
                # If no link found, try to get it from parent or data attributes
                try:
                    parent = element.find_element(By.XPATH, "./..")
                    link = parent.find_element(By.TAG_NAME, "a")
                    href = link.get_attribute('href')
                    if href:
                        listing['platform_url'] = href if href.startswith('http') else f"https://es.wallapop.com{href}"
                except:
                    pass
            
            # Extract image
            listing['image_url'] = ''
            img_selectors = [
                (By.TAG_NAME, "img"),
                (By.CSS_SELECTOR, "img[class*='image']"),
                (By.CSS_SELECTOR, "img[class*='Image']"),
            ]
            
            for by, selector in img_selectors:
                try:
                    img_elem = element.find_element(by, selector)
                    src = img_elem.get_attribute('src') or img_elem.get_attribute('data-src') or img_elem.get_attribute('data-lazy-src')
                    if src and 'wallapop' in src.lower():
                        listing['image_url'] = src
                        break
                except:
                    continue
            
            # Try to extract vehicle details from title/description
            combined_text = f"{listing.get('title', '')} {listing.get('description', '')}".lower()
            
            # Extract year (look for 4-digit numbers between 1990-2025)
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
            
            # Only return if we have at least a title
            if listing.get('title') and listing['title'] != f"Listing {index + 1}":
                logger.debug(f"Extracted listing: {listing.get('title', 'Unknown')} - {listing.get('price', 0)}€")
                return listing
            
            return None
            
        except Exception as e:
            logger.error(f"Error in _extract_listing_data: {e}", exc_info=True)
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
