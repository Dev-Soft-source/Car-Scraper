from re import search
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
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

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
            chrome_options.add_argument('--headless')  # Use headless mode if set
        
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument('--no-sandbox')  # Required in Docker
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument('--disable-dev-shm-usage')  # Prevents crashes in Docker
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--window-size=1920,1080')
        
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
            # Install ChromeDriver with WebDriverManager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)  # Allow more time for Chrome to initialize
            
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
        # Category filter
        if search_criteria.get('category'):
            params.append(f"category_id={search_criteria['category']}")

        # Brand / make filter 
        if search_criteria.get('make'): 
            brand = search_criteria['make'].replace(" ", "+") 
            params.append(f"brand={brand}")

        if search_criteria.get('model'):
            params.append(f"model={search_criteria['model']}")

        # Price filter
        if search_criteria.get('price_min'):
            params.append(f"min_sale_price={int(search_criteria['price_min'])}")

        if search_criteria.get('price_max'):
            params.append(f"max_sale_price={int(search_criteria['price_max'])}")   

        # year filter
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
        # Construct URL
        search_url = f"{base_url}/search?{'&'.join(params)}&source=side_bar_filters&order_by=most_relevance"
       
        return search_url
    
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
            logger.info(f"Navigating to: {search_criteria['site_url']}")
            
            # Navigate to the page
            if not self.driver:
                raise Exception("WebDriver not initialized")
            self.driver.get(search_criteria['site_url'])
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
            #self._select_category(search_criteria['site_url'], search_criteria['keyword'])

            search_url = self._build_search_url(search_criteria['site_url'], search_criteria)

            try:
                self.driver.get(search_url)
            except Exception as e:
                logger.warning(f"Search Page load timeout, but continuing: {e}")

            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                logger.info("Page loaded successfully")
            except Exception as e:
                logger.warning(f"Page load timeout, but continuing: {e}")

            print("Search_url: ", search_url)
            
            # Scroll to load more content
            self._scroll_page()

            # --- Wait until at least one item appears ---
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/item/']"))
                )
            except Exception as e:
                print("No listings found or page took too long to load.")
                self.driver.quit()
                exit()

            # --- Collect all listing links ---
            listing_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/item/']")
            listing_urls = [elem.get_attribute("href") for elem in listing_elements]

            print(f"Total listings found: {len(listing_urls)}")
            for index, url in enumerate(listing_urls[:50]):  # limit to 50
                if not isinstance(url, str) or url is None:
                    logger.warning(f"Skipping invalid URL at index {index}: {url}")
                    continue
                listings.append(self._extract_listing_data(url, index))
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
            
            # >>> Navigate to the category URL
            try:
                self.driver.get(cate_url)
                self._human_delay(1, 4)
                self._scroll_page()
                self._human_delay(1, 4)
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
    
    def _extract_listing_data(self, url, index):

        listing = {"url": url}

        # ----- platform_id -----
        match_url = re.search(r'/item/([^/]+)', url)
        if match_url:
            listing["platform_id"] = match_url.group(1)
            print(f"Item ID: {listing["platform_id"]}")
        else:
            listing["platform_id"] = None

        if not self.driver:
            return None
        try:
            self.driver.get(url)
            self._human_delay(3, 5)

            # Wait for main body
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Get rendered body HTML
            body_html = self.driver.execute_script("return document.body.innerHTML")
            self._human_delay(1, 2)

            # Parse HTML
            soup = BeautifulSoup(body_html, "html.parser")

            # --- TITLE ---
            # Find h1 with class containing 'ItemDetailTwoColumns__title'
            title_tag = None
            for h1 in soup.find_all("h1"):
                h1_class = h1.get("class")
                if h1_class and any("ItemDetailTwoColumns__title" in c for c in h1_class):
                    title_tag = h1
                    break
            listing["title"] = title_tag.get_text(strip=True) if title_tag else None

            all_span = soup.find_all("span")
            # --- PRICE ---
            price_tag = None
            for h1 in all_span:
                h1_class = h1.get("class")
                if h1_class and any("price_ItemDetailPrice" in c for c in h1_class):
                    price_tag = h1
                    break
            if price_tag:
                value = price_tag.get_text(strip=True) 
                listing["price"] = value.replace("\xa0", "").replace("€", "").replace(".", "").strip()
            else:         
                listing["price"] = None 

            # --- SELLER, POWER ---
            seller_tag = None
            for h1 in all_span:
                h1_class = h1.get("class")
                if h1_class and any("profile_ItemDetailSellerProfile__name" in c for c in h1_class):
                    seller_tag = h1
                    break
            listing["seller"] = seller_tag.get_text(strip=True) if seller_tag else None

            attributes = []

            for span in all_span:
                span_class = span.get("class")
                if span_class and any("AttributesInfo__measure" in c for c in span_class):
                    attributes.append(span.get_text(strip=True))


            listing["fuel_type"] = attributes[3] if len(attributes) > 3 else None
            if len(attributes) > 4:
                hp = attributes[4]
                listing["power"] = hp.replace(" caballos", "").strip()
            else:
                listing["power"] = None
            # ItemDetailSEOBubble__link      

            # --- MAKER ---
            maker_tag = None
            for h1 in all_span:
                h1_class = h1.get("class")
                if h1_class and any("bubble_ItemDetailSEOBubble__link" in c for c in h1_class):
                    maker_tag = h1
                    break
            listing["make"] = maker_tag.get_text(strip=True) if maker_tag else None

            # --- MODEL, YEAR, MILEAGE ---
            # Defensive lookups for ['model', 'year', 'mileage'] to avoid attribute errors
            def get_attribute_value(label):
                label_span = soup.find('span', string=label)
                if label_span:
                    value_span = label_span.find_next('span')
                    if value_span and hasattr(value_span, 'text'):
                        return value_span.text.strip()
                return None

            listing["model"] = get_attribute_value('Modelo')
            listing["year"] = get_attribute_value('Año')
            listing["mileage"] = get_attribute_value('Kilómetros')

            # --- DESCRIPTION ---
            all_section = soup.find_all("section")
            description_tag = None
            for h1 in all_section:
                h1_class = h1.get("class")
                if h1_class and any("ItemDetailTwoColumns__description" in c for c in h1_class):
                    description_tag = h1
                    break
            listing["description"] = description_tag.get_text(strip=True) if description_tag else None

            # --- EDITED LAST TIME ---

            last_time_tag = None
            for h1 in all_span:
                h1_class = h1.get("class")
                if h1_class and any("stats_ItemDetailStats__description" in c for c in h1_class):
                    last_time_tag = h1
                    break
            if last_time_tag:
                last = last_time_tag.get_text(strip=True)
                # Regular expression to extract the time (number and unit)
                match = re.search(r"Editado hace (\d+) (\w+)", last)

                if match:
                    number = int(match.group(1))  # Extracts the number
                    unit = match.group(2)         # Extracts the unit (days, months, etc.)

                    # Get the current UTC time
                    current_utc_time = datetime.utcnow()

                    # Subtract the time based on the unit
                    if unit == "días":
                        time_difference = timedelta(days=number)
                    elif unit == "horas":
                        time_difference = timedelta(hours=number)
                    elif unit == "minutos":
                        time_difference = timedelta(minutes=number)
                    else:
                        listing["last_updated"] = None
                    # Calculate the UTC time before the given duration, only if unit was handled above
                    if unit in ["días", "horas", "minutos"]:
                        original_time = current_utc_time - time_difference
                        listing["last_updated"] = original_time.strftime('%Y-%m-%d %H:%M:%S.%f')
                    else:
                        listing["last_updated"] = None

            # --- IMAGE URL ---
            # Try to find the first img tag with slot="carousel-content"
            img_tag = soup.find('img', {'slot': 'carousel-content'})

            # Check if the img_tag exists and has a 'src' attribute
            if img_tag and img_tag.has_attr('src'):
                listing["image_url"] = img_tag['src']
            else:
                listing["image_url"] = None

        except Exception as e:
            print("Failed to get title:", e)
            return None

        return listing

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
