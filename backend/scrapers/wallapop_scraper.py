from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

logging.basicConfig(level=logging.INFO)
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
        """Initialize Chrome WebDriver for selenium/standalone-chrome"""

        chrome_options = Options()

        # ----- HEADLESS -----
        if self.headless:
            chrome_options.add_argument("--headless=new")

        # ----- BASIC OPTIONS -----
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--remote-debugging-port=9222")

        # ----- USER AGENT -----
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        )

        # ----- LANG & PREFS -----
        chrome_options.add_argument("--lang=es-ES")
        chrome_options.add_experimental_option("prefs", {
            "intl.accept_languages": "es-ES,es;q=0.9,en;q=0.8",
            "profile.default_content_setting_values.notifications": 2,
            "profile.managed_default_content_settings.images": 1,
        })

        # ----- REMOVE AUTOMATION FLAGS -----
        chrome_options.add_experimental_option(
            "excludeSwitches", ["enable-automation", "enable-logging"]
        )
        chrome_options.add_experimental_option("useAutomationExtension", False)

        try:
            # ***********************************************
            # ❗ THE MOST IMPORTANT FIX
            # Use Remote WebDriver instead of ChromeDriver
            # ***********************************************
            self.driver = webdriver.Remote(
                command_executor="http://localhost:4444/wd/hub",
                options=chrome_options
            )

            self.driver.set_page_load_timeout(60)

            # ----- STEALTH -----
            stealth_js = """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
                Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es']});
                window.chrome = { runtime: {} };
            """

            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": stealth_js}
            )

            logger.info("✓ Chrome WebDriver initialized successfully")
            return True

        except Exception as e:
            logger.error(f"✗ Failed to initialize WebDriver: {e}")
            raise


    def _human_delay(self, min_seconds: float = 2, max_seconds: float = 5):
        """Add random delay to simulate human behavior"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _random_mouse_movement(self):
        """Simulate random mouse movements"""
        if not self.driver:
            return
        try:
            actions = ActionChains(self.driver)
            for _ in range(random.randint(2, 4)):
                x_offset = random.randint(-100, 100)
                y_offset = random.randint(-100, 100)
                actions.move_by_offset(x_offset, y_offset)
            actions.perform()
        except Exception as e:
            logger.debug(f"Mouse movement simulation failed: {e}")
    
    def _handle_cookie_consent(self):
        """Handle cookie consent dialogs"""
        if not self.driver:
            return False
        try:
            time.sleep(3)
            
            # Try multiple selectors
            selectors = [
                "//button[contains(text(), 'Aceptar')]",
                "//button[contains(text(), 'Accept')]",
                "//button[contains(@id, 'accept')]",
                "//button[contains(@class, 'accept')]",
            ]
            
            for selector in selectors:
                try:
                    button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    self._human_delay(1, 2)
                    button.click()
                    logger.info("✓ Cookie consent handled")
                    self._human_delay(2, 4)
                    return True
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"No cookie consent dialog found: {e}")
        
        return False
    
    def _build_search_url(self, base_url: str, search_criteria: Dict) -> str:
        """Build Wallapop search URL from criteria"""
        params = []
        
        if search_criteria.get('category'):
            params.append(f"category_id={search_criteria['category']}")

        if search_criteria.get('make'): 
            brand = search_criteria['make'].replace(" ", "+") 
            params.append(f"brand={brand}")

        if search_criteria.get('model'):
            model = search_criteria['model'].replace(" ", "+")
            params.append(f"model={model}")

        if search_criteria.get('price_min'):
            params.append(f"min_sale_price={int(search_criteria['price_min'])}")

        if search_criteria.get('price_max'):
            params.append(f"max_sale_price={int(search_criteria['price_max'])}")

        if search_criteria.get('year_from'):
            params.append(f"min_year={int(search_criteria['year_from'])}")

        if search_criteria.get('year_to'):
            params.append(f"max_year={int(search_criteria['year_to'])}")

        if search_criteria.get('mileage_max'):
            mileage_max = int(search_criteria['mileage_max'])
            if mileage_max < 250000:
                params.append(f"max_km={mileage_max}")
                
        if search_criteria.get('power'):
            params.append(f"max_horse_power={int(search_criteria['power'])}")
            
        search_url = f"{base_url}/search?{'&'.join(params)}&source=side_bar_filters&order_by=most_relevance"
        return search_url
    
    def scrape_listings(self, search_criteria: Dict, max_listings: int = 50) -> List[Dict]:
        """Scrape Wallapop listings with enhanced error handling"""
        
        if self.driver is None:
            self._init_driver()
        
        listings = []
        
        try:
            # Navigate to homepage first (more natural)
            logger.info("→ Loading Wallapop homepage...")
            self.driver.get(search_criteria['site_url'])
            self._human_delay(4, 6)
            
            # Handle cookies
            self._handle_cookie_consent()
            
            # Simulate human interaction
            self._random_mouse_movement()
            self._scroll_page(scrolls=2)
            
            # Build and navigate to search URL
            search_url = self._build_search_url(search_criteria['site_url'], search_criteria)
            logger.info(f"→ Navigating to search: {search_url}")
            
            self.driver.get(search_url)
            self._human_delay(5, 8)
            
            # Wait for listings to load
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/item/']"))
                )
                logger.info("✓ Listings loaded successfully")
            except Exception as e:
                logger.error(f"✗ No listings found: {e}")
                return listings
            
            # Scroll to load more listings
            self._scroll_page(scrolls=3)
            self._human_delay(3, 5)
            
            # Collect listing URLs
            listing_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/item/']")
            listing_urls = list(set([elem.get_attribute("href") for elem in listing_elements if elem.get_attribute("href")]))
            
            logger.info(f"✓ Found {len(listing_urls)} unique listings")
            
            # Extract data from each listing
            for index, url in enumerate(listing_urls[:max_listings], 1):
                try:
                    logger.info(f"→ Processing listing {index}/{min(max_listings, len(listing_urls))}")
                    
                    if not isinstance(url, str) or not url:
                        logger.warning(f"  ✗ Invalid URL at index {index}")
                        continue
                    
                    listing_data = self._extract_listing_data(url)
                    
                    if listing_data:
                        listings.append(listing_data)
                        logger.info(f"  ✓ {listing_data.get('title', 'Unknown')[:50]}")
                    else:
                        logger.warning(f"  ✗ No data extracted")
                    
                    # Random delay between requests
                    self._human_delay(3, 6)
                    
                except Exception as e:
                    logger.error(f"  ✗ Failed to process listing {index}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"✗ Scraping error: {e}", exc_info=True)
        
        logger.info(f"\n✓ Successfully scraped {len(listings)} listings")
        return listings
    
    def _scroll_page(self, scrolls: int = 3):
        """Scroll page gradually to simulate human behavior"""
        if not self.driver:
            return
        try:
            for i in range(scrolls):
                # Scroll to a random position
                scroll_height = self.driver.execute_script("return document.body.scrollHeight")
                scroll_to = random.randint(
                    int(scroll_height * (i / scrolls)),
                    int(scroll_height * ((i + 1) / scrolls))
                )
                self.driver.execute_script(f"window.scrollTo(0, {scroll_to});")
                self._human_delay(2, 4)
                
        except Exception as e:
            logger.warning(f"Scroll error: {e}")

    def _clean_int(self, value: Optional[str]) -> int:
        """Convert scraped strings to integers safely"""
        if not value:
            return 0
        value = (
            value.replace(".", "")
                .replace(",", "")
                .replace("€", "")
                .replace("km", "")
                .replace("caballos", "")
                .replace(" ", "")
                .strip()
        )
        try:
            return int(value) if value.isdigit() else 0
        except:
            return 0
    
    def _extract_listing_data(self, url: str) -> Optional[Dict]:
        """Extract data from a single listing page"""
        
        listing = {"url": url}
        
        # Extract platform_id from URL
        match_url = re.search(r'/item/([^/?]+)', url)
        if match_url:
            listing["platform_id"] = match_url.group(1) if match_url else ""
            if not self.driver:
                return None
        try:
            self.driver.get(url)
            self._human_delay(4, 6)
            
            # Wait for page load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get HTML and parse
            body_html = self.driver.execute_script("return document.body.innerHTML")
            soup = BeautifulSoup(body_html, "html.parser")
            
            # Extract title
            title_tag = soup.find("h1", class_=lambda x: x and "ItemDetailTwoColumns__title" in str(x))
            listing["title"] = title_tag.get_text(strip=True) if title_tag else None
            
            # Extract price
            all_span = soup.find_all("span")
            listing["price"] = None
            for span in all_span:
                span_class = span.get("class", [])
                if any("price_ItemDetailPrice" in str(c) for c in span_class):
                    value = span.get_text(strip=True)
                    clean_value = value.replace("\xa0", "").replace("€", "").replace(".", "").strip()
                    listing["price"] = self._clean_int(clean_value)
                    break
            
            # Extract seller
            seller_tag = soup.find("span", class_=lambda x: x and "profile_ItemDetailSellerProfile__name" in str(x))
            listing["seller"] = seller_tag.get_text(strip=True) if seller_tag else None
            
            # Extract fuel type
            gas_icon = soup.find("walla-icon", {"icon": "gasoline"})
            if gas_icon:
                span = gas_icon.find_next("span")
                listing["fuel_type"] = span.get_text(strip=True) if span else None
            else:
                listing["fuel_type"] = None
            
            # Extract power
            pow_icon = soup.find("walla-icon", {"icon": "piston"})
            if pow_icon:
                span = pow_icon.find_next("span")
                if span:
                    listing["power"] = self._clean_int(span.get_text(strip=True))
                else:
                    listing["power"] = 0
            else:
                listing["power"] = 0
            
            # Extract location
            loc_icon = soup.find("walla-icon", {"icon": "location"})
            if loc_icon:
                span = loc_icon.find_next("span")
                listing["location"] = span.get_text(strip=True) if span else ""
            else:
                listing["location"] = ""
            
            # Extract make
            maker_tag = soup.find("span", class_=lambda x: x and "bubble_ItemDetailSEOBubble__link" in str(x))
            listing["make"] = maker_tag.get_text(strip=True) if maker_tag else None
            
            # Extract model, year, mileage
            def get_attribute_value(label):
                label_span = soup.find('span', string=lambda x: x and label in x)
                if label_span:
                    value_span = label_span.find_next('span')
                    if value_span:
                        return value_span.get_text(strip=True)
                return None
            
            listing["model"] = get_attribute_value('Modelo')
            listing["year"] = self._clean_int(get_attribute_value('Año'))
            listing["mileage"] = self._clean_int(get_attribute_value('Kilómetros'))
            
            # Extract description
            description_tag = soup.find("section", class_=lambda x: x and "ItemDetailTwoColumns__description" in str(x))
            listing["description"] = description_tag.get_text(strip=True) if description_tag else None
            
            # Extract last updated time
            time_tag = soup.find("span", class_=lambda x: x and "stats_ItemDetailStats__description" in str(x))
            if time_tag:
                time_text = time_tag.get_text(strip=True)
                listing["last_updated"] = self._parse_relative_date(time_text)
            else:
                listing["last_updated"] = None
            
            # Extract image URL
            img_tag = soup.find('img', {'slot': 'carousel-content'})
            listing["image_url"] = img_tag.get('src') if img_tag and img_tag.has_attr('src') else None
            
            return listing
            
        except Exception as e:
            logger.error(f"Failed to extract data from {url}: {e}")
            return None
    
    def _parse_relative_date(self, text: str) -> Optional[str]:
        """Parse relative dates like 'Editado hace 3 días'"""
        patterns = {
            r'(\d+)\s*minuto': lambda n: timedelta(minutes=int(n)),
            r'(\d+)\s*hora': lambda n: timedelta(hours=int(n)),
            r'(\d+)\s*día': lambda n: timedelta(days=int(n)),
            r'(\d+)\s*semana': lambda n: timedelta(weeks=int(n)),
        }
        
        for pattern, delta_func in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    time_delta = delta_func(match.group(1))
                    original_time = datetime.utcnow() - time_delta
                    return original_time.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    logger.error(f"Date parsing error: {e}")
        
        return None
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✓ WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
    
    def __enter__(self):
        """Context manager entry"""
        self._init_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Main execution


# if __name__ == "__main__":
#     criteria = {
#         "site_url": "https://es.wallapop.com",
#         "keyword": "Coches",
#         "category": "100",  # Cars category
#         # Optional filters:
#         # "make": "Audi",
#         # "model": "A3",
#         # "price_max": 15000,
#         # "year_from": 2015,
#         # "mileage_max": 150000,
#     }
    
#     # Use context manager for automatic cleanup
#     with WallapopScraper(headless=False) as scraper:
#         results = scraper.scrape_listings(criteria, max_listings=10)
        
#         print(f"\n{'='*60}")
#         print(f"SCRAPING COMPLETE: {len(results)} listings")
#         print(f"{'='*60}\n")
        
#         for i, listing in enumerate(results, 1):
#             print(f"{i}. {listing.get('title', 'N/A')}")
#             print(f"   Price: {listing.get('price', 0)}€")
#             print(f"   Year: {listing.get('year', 'N/A')} | Mileage: {listing.get('mileage', 0)} km")
#             print(f"   URL: {listing.get('url', 'N/A')}")
#             print()