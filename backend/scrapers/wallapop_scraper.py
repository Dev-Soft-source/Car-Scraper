# updated_wallapop_and_service.py
import os
import time
import random
import logging
import json
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException

from bs4 import BeautifulSoup

# Database/service imports (adjust to your project)
from backend.database.config import SessionLocal
from models.models import Search, Listing, Log, Statistics, UserSettings

# For sending email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

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
    def __init__(self, headless: bool = True, chromium_path: Optional[str] = None):
        self.headless = headless
        self.driver = None
        self.chromium_path = chromium_path
        # Maximum times to try recreating the driver when session invalid
        self._driver_create_attempts = 0
        self._max_driver_create_attempts = 3

    def _init_driver(self) -> None:
        """Initialize Selenium WebDriver with Chromium. Raises on fatal error."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--lang=es-ES")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        )

        if self.chromium_path:
            chrome_options.binary_location = self.chromium_path

        try:
            driver_path = ChromeDriverManager().install()
            self.driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
            self.driver.set_page_load_timeout(60)
            self._driver_create_attempts = 0
            logger.info(f"✓ Chromium WebDriver initialized successfully using driver: {driver_path}")
        except Exception as e:
            self._driver_create_attempts += 1
            logger.error(f"✗ Failed to initialize WebDriver (attempt {self._driver_create_attempts}): {e}")
            # Reraise for the caller to decide
            raise

    def _ensure_driver(self) -> None:
        """
        Ensure a live driver is available. If the session is invalid or driver has crashed,
        try to recreate it up to _max_driver_create_attempts times.
        """
        # If there's no driver, create one
        if self.driver is None:
            logger.debug("Driver not present, creating a new WebDriver instance.")
            self._init_driver()
            return

        # Test driver session with a lightweight operation
        try:
            # Accessing session_id or title will raise if session invalid
            _ = self.driver.session_id
            # Optional ping: self.driver.title
        except (InvalidSessionIdException, WebDriverException) as e:
            logger.warning(f"Driver session invalid or crashed: {e}. Restarting driver.")
            try:
                try:
                    self.driver.quit()
                except Exception:
                    pass
            finally:
                self.driver = None

            # Attempt to recreate driver, with limited retries
            if self._driver_create_attempts < self._max_driver_create_attempts:
                self._driver_create_attempts += 1
                self._init_driver()
            else:
                raise RuntimeError("Exceeded attempts to recreate WebDriver")

    def _human_delay(self, min_seconds: float = 2, max_seconds: float = 5):
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)

    def _random_mouse_movement(self):
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
        if not self.driver:
            return False
        try:
            time.sleep(3)
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
                except Exception:
                    continue
        except Exception as e:
            logger.debug(f"No cookie consent dialog found: {e}")
        return False

    def _build_search_url(self, base_url: str, search_criteria: Dict) -> str:
        params = []
        if search_criteria.get('category'):
            params.append(f"category_id={search_criteria['category']}")
        if search_criteria.get('make'):
            brand = str(search_criteria['make']).replace(" ", "+")
            params.append(f"brand={brand}")
        if search_criteria.get('model'):
            model = str(search_criteria['model']).replace(" ", "+")
            params.append(f"model={model}")
        if search_criteria.get('fuel_type'):
            params.append(f"engine={search_criteria['fuel_type']}")
        if search_criteria.get('price_min') is not None:
            try:
                params.append(f"min_sale_price={int(search_criteria['price_min'])}")
            except Exception:
                pass
        if search_criteria.get('price_max') is not None:
            try:
                params.append(f"max_sale_price={int(search_criteria['price_max'])}")
            except Exception:
                pass
        if search_criteria.get('year_from') is not None:
            try:
                params.append(f"min_year={int(search_criteria['year_from'])}")
            except Exception:
                pass
        if search_criteria.get('year_to') is not None:
            try:
                params.append(f"max_year={int(search_criteria['year_to'])}")
            except Exception:
                pass
        if search_criteria.get('mileage_max') is not None:
            try:
                mileage_max = int(search_criteria['mileage_max'])
                if mileage_max < 250000:
                    params.append(f"max_km={mileage_max}")
            except Exception:
                pass
        if search_criteria.get('power') is not None:
            try:
                params.append(f"max_horse_power={int(search_criteria['power'])}")
            except Exception:
                pass

        query = "&".join(params)
        if query:
            search_url = f"{base_url}/search?{query}&source=side_bar_filters&order_by=most_relevance"
        else:
            search_url = f"{base_url}/search?source=side_bar_filters&order_by=most_relevance"
        return search_url

    def scrape_listings(self, search_criteria: Dict, max_listings: int = 50) -> List[Dict]:
        listings = []
        try:
            # Ensure driver present and healthy
            try:
                self._ensure_driver()
            except Exception as e:
                logger.error(f"Unable to ensure WebDriver: {e}")
                return listings

            logger.info("→ Loading Wallapop homepage...")
            try:
                # Try visiting site_url with retry for transient driver issues
                for attempt in range(3):
                    try:
                        self.driver.get(search_criteria['site_url'])
                        break
                    except (InvalidSessionIdException, WebDriverException) as e:
                        logger.warning(f"Driver failed to load homepage (attempt {attempt+1}): {e}")
                        # Attempt recreate
                        try:
                            self.driver.quit()
                        except Exception:
                            pass
                        self.driver = None
                        self._init_driver()
                else:
                    logger.error("Failed to load homepage after retries")
                    return listings
            except Exception as e:
                logger.error(f"Error navigating to homepage: {e}")
                return listings

            self._human_delay(4, 6)
            self._handle_cookie_consent()
            self._random_mouse_movement()
            self._scroll_page(scrolls=2)

            # Build and navigate to search URL
            search_url = self._build_search_url(search_criteria['site_url'], search_criteria)
            logger.info(f"→ Navigating to search: {search_url}")

            try:
                self.driver.get(search_url)
            except (InvalidSessionIdException, WebDriverException) as e:
                logger.warning(f"Driver failed navigating to search url: {e}. Trying to recreate driver and retry once.")
                try:
                    try:
                        self.driver.quit()
                    except Exception:
                        pass
                    self.driver = None
                    self._init_driver()
                    self.driver.get(search_url)
                except Exception as e2:
                    logger.error(f"Failed to navigate to search URL after driver restart: {e2}")
                    return listings

            self._human_delay(5, 8)

            # Wait for listings
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/item/']"))
                )
                logger.info("✓ Listings loaded successfully")
            except Exception as e:
                logger.error(f"✗ No listings found: {e}")
                return listings

            self._scroll_page(scrolls=3)
            self._human_delay(3, 5)

            listing_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/item/']")
            listing_urls = list({elem.get_attribute("href") for elem in listing_elements if elem.get_attribute("href")})
            logger.info(f"✓ Found {len(listing_urls)} unique listings")

            for index, url in enumerate(listing_urls[:max_listings], 1):
                try:
                    logger.info(f"→ Processing listing {index}/{min(max_listings, len(listing_urls))}")
                    if not isinstance(url, str) or not url:
                        logger.warning(f"  ✗ Invalid URL at index {index}")
                        continue

                    listing_data = self._extract_listing_data(url, index)
                    if listing_data:
                        listings.append(listing_data)
                        logger.info(f"  ✓ {listing_data.get('title', 'Unknown')[:50]}")
                    else:
                        logger.warning("  ✗ No data extracted")
                    self._human_delay(3, 6)
                except Exception as e:
                    logger.error(f"  ✗ Failed to process listing {index}: {e}", exc_info=True)
                    continue

        except Exception as e:
            logger.error(f"✗ Scraping error: {e}", exc_info=True)

        logger.info(f"\n✓ Successfully scraped {len(listings)} listings")
        return listings

    def _scroll_page(self, scrolls: int = 3):
        if not self.driver:
            return
        try:
            for i in range(scrolls):
                scroll_height = self.driver.execute_script("return document.body.scrollHeight")
                scroll_to = random.randint(
                    int(scroll_height * (i / scrolls)),
                    int(scroll_height * ((i + 1) / scrolls))
                )
                self.driver.execute_script(f"window.scrollTo(0, {scroll_to});")
                self._human_delay(2, 4)
        except Exception as e:
            logger.warning(f"Scroll error: {e}")

    def _clean_int(self, value: Optional[str]) -> Optional[int]:
        """Convert scraped strings to integers safely. Return None when value is not parseable."""
        if value is None:
            return None
        try:
            value_str = str(value)
            # Remove common symbols and whitespace
            cleaned = (
                value_str.replace(".", "")
                         .replace(",", "")
                         .replace("€", "")
                         .replace("km", "")
                         .replace("caballos", "")
                         .replace(" ", "")
                         .strip()
            )
            if cleaned == "":
                return None
            # Extract digits possibly with sign
            match = re.search(r'-?\d+', cleaned)
            if not match:
                return None
            return int(match.group(0))
        except Exception:
            return None

    def _extract_listing_data(self, url, index):
        listing = {"url": url}
        # ----- platform_id -----
        match_url = re.search(r'/item/([^/]+)', url)
        if match_url:
            listing["platform_id"] = match_url.group(1)
            print(f'Item ID: {listing["platform_id"]}')
        else:
            listing["platform_id"] = None

        if not self.driver:
            # If driver was closed, try to create it
            try:
                self._init_driver()
            except Exception as e:
                logger.error(f"Unable to initialize driver for extracting listing: {e}")
                return None

        try:
            # Protect navigation with ensure-driver and lightweight retry
            try:
                self._ensure_driver()
                self.driver.get(url)
            except (InvalidSessionIdException, WebDriverException):
                logger.warning("Driver invalid while opening listing. Recreating driver and retrying once.")
                try:
                    try:
                        self.driver.quit()
                    except Exception:
                        pass
                    self.driver = None
                    self._init_driver()
                    self.driver.get(url)

                    self._human_delay(4, 6)
                    self._handle_cookie_consent()
                    self._random_mouse_movement()
                    self._scroll_page(scrolls=2)
                except Exception as e2:
                    logger.error(f"Failed to open listing after driver restart: {e2}")
                    return None

            self._human_delay(5, 7)
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            body_html = self.driver.execute_script("return document.body.innerHTML")
            self._human_delay(2, 5)
            soup = BeautifulSoup(body_html, "html.parser")

            # --- TITLE ---
            title_tag = None
            for h1 in soup.find_all("h1"):
                h1_class = h1.get("class")
                if h1_class and any("ItemDetailTwoColumns__title" in c for c in h1_class):
                    title_tag = h1
                    break
            listing["title"] = title_tag.get_text(strip=True) if title_tag else None

            all_span = soup.find_all("span")

            # --- PRICE ---
            listing["price"] = None
            for span in all_span:
                span_class = span.get("class")
                if span_class and any("price_ItemDetailPrice" in c for c in span_class):
                    value = span.get_text(strip=True)
                    only_value = value.replace("\xa0", "").replace("€", "").strip()
                    parsed = self._clean_int(only_value)
                    if parsed is not None:
                        listing["price"] = parsed
                        break

            # --- SELLER ---
            seller_tag = None
            for span in all_span:
                span_class = span.get("class")
                if span_class and any("profile_ItemDetailSellerProfile__name" in c for c in span_class):
                    seller_tag = span
                    break
            listing["seller"] = seller_tag.get_text(strip=True) if seller_tag else None

            # --- FUEL_TYPE ---
            gas_icon = soup.find("walla-icon", {"icon": "gasoline"})
            if gas_icon:
                span = gas_icon.find_next("span")
                listing["fuel_type"] = span.get_text(strip=True) if span else None
            else:
                listing["fuel_type"] = None

            # --- POWER ---
            pow_icon = soup.find("walla-icon", {"icon": "piston"})
            if pow_icon:
                span = pow_icon.find_next("span")
                if span:
                    tmp_pow = span.get_text(strip=True)
                    listing["power"] = self._clean_int(tmp_pow) or 0
                else:
                    listing["power"] = 0
            else:
                listing["power"] = 0

            # --- LOCATION ---
            loc_icon = soup.find("walla-icon", {"icon": "location"})
            if loc_icon:
                span = loc_icon.find_next("a")
                listing["location"] = span.get_text(strip=True) if span else None
            else:
                listing["location"] = ""

            # --- MAKER ---
            maker_tag = None
            for span in all_span:
                span_class = span.get("class")
                if span_class and any("bubble_ItemDetailSEOBubble__link" in c for c in span_class):
                    maker_tag = span
                    break
            listing["make"] = maker_tag.get_text(strip=True) if maker_tag else None

            # --- MODEL, YEAR, MILEAGE ---
            def get_attribute_value(label):
                try:
                    label_span = soup.find('span', string=label)
                    if label_span:
                        value_span = label_span.find_next('span')
                        if value_span and hasattr(value_span, 'text'):
                            return value_span.text.strip()
                except Exception:
                    pass
                return None

            listing["model"] = get_attribute_value('Modelo')
            listing["year"] = self._clean_int(get_attribute_value('Año'))
            listing["mileage"] = self._clean_int(get_attribute_value('Kilómetros'))

            # --- DESCRIPTION ---
            description_tag = None
            for section in soup.find_all("section"):
                section_class = section.get("class")
                if section_class and any("ItemDetailTwoColumns__description" in c for c in section_class):
                    description_tag = section
                    break
            listing["description"] = description_tag.get_text(strip=True) if description_tag else None

            # --- EDITED LAST TIME ---
            last_time_tag = None
            for span in all_span:
                span_class = span.get("class")
                if span_class and any("stats_ItemDetailStats__description" in c for c in span_class):
                    last_time_tag = span
                    break
            if last_time_tag:
                last = last_time_tag.get_text(strip=True)
                parsed_relative = self._parse_relative_date(last)
                listing["last_updated"] = parsed_relative
            else:
                listing["last_updated"] = None

            # --- IMAGE URL ---
            img_tag = soup.find('img', {'slot': 'carousel-content'})
            if img_tag and img_tag.has_attr('src'):
                listing["image_url"] = img_tag['src']
            else:
                listing["image_url"] = None

        except Exception as e:
            logger.error(f"Failed to extract listing data for {url}: {e}", exc_info=True)
            return None

        return listing

    def _parse_relative_date(self, text: str) -> Optional[str]:
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
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✓ WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None

    def __enter__(self):
        self._init_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ---------------------------
# ScrapingService (with Gmail notifications)
# ---------------------------
class ScrapingService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.active_jobs = {}  # search_id -> job_id mapping
        self.scrapers = {}  # search_id -> scraper instance

        # Email configuration from env
        self.gmail_from = os.environ.get("GMAIL_EMAIL")
        self.gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scraping scheduler started")

    def stop(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scraping scheduler stopped")

    def _send_gmail_notification(self, to_email: str, subject: str, body: str, html: Optional[str] = None):
        """
        Send email with retries and exponential backoff.
        Expects GMAIL_EMAIL and GMAIL_APP_PASSWORD environment variables to be set.
        """
        if not self.gmail_from or not self.gmail_app_password:
            logger.error("Gmail credentials are not configured. Set GMAIL_EMAIL and GMAIL_APP_PASSWORD env vars.")
            return False

        msg = MIMEMultipart("alternative")
        msg["From"] = self.gmail_from
        msg["To"] = to_email
        msg["Subject"] = subject
        part_text = MIMEText(body, "plain")
        msg.attach(part_text)
        if html:
            part_html = MIMEText(html, "html")
            msg.attach(part_html)

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                server = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
                server.starttls()
                server.login(self.gmail_from, self.gmail_app_password)
                server.sendmail(self.gmail_from, to_email, msg.as_string())
                server.quit()
                logger.info(f"Notification email sent to {to_email}")
                return True
            except smtplib.SMTPAuthenticationError as auth_err:
                # Usually 535: bad credentials - inform user (no retry)
                logger.error(f"SMTP auth error: {auth_err} - check GMAIL_APP_PASSWORD/app password & GMAIL_EMAIL.")
                return False
            except Exception as e:
                logger.warning(f"Failed to send email on attempt {attempt}: {e}")
                if attempt < max_attempts:
                    backoff = 2 ** attempt
                    time.sleep(backoff)
                else:
                    logger.error("Exceeded email send attempts.")
                    return False

    def start_search_scraping(self, search_id: str, user_id: str, interval_minutes: int = 60):
        if search_id in self.active_jobs:
            logger.warning(f"Scraping already active for search {search_id}")
            return False

        try:
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
        if search_id not in self.active_jobs:
            logger.warning(f"No active scraping for search {search_id}")
            return False
        try:
            job_id = self.active_jobs[search_id]
            self.scheduler.remove_job(job_id)
            del self.active_jobs[search_id]
            if search_id in self.scrapers:
                try:
                    self.scrapers[search_id].close()
                except Exception:
                    pass
                del self.scrapers[search_id]
            logger.info(f"Stopped scraping for search {search_id}")
            return True
        except Exception as e:
            logger.error(f"Error stopping scraping for search {search_id}: {e}")
            return False

    def _scrape_search(self, search_id: str, user_id: str):
        db = SessionLocal()
        search = None
        try:
            search = db.query(Search).filter(Search.id == search_id, Search.user_id == user_id).first()
            if search is None or not bool(search.is_active):
                logger.warning(f"Search {search_id} not found or inactive")
                return

            # Ensure scraper instance exists
            if search_id not in self.scrapers:
                try:
                    self.scrapers[search_id] = WallapopScraper(headless=True)
                except Exception as e:
                    logger.error(f"Failed creating scraper for {search_id}: {e}")
                    return

            scraper = self.scrapers[search_id]

            # Build criteria dict
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

            logger.info(f"Scraping with criteria: {search_criteria}")
            scraped_listings = []
            try:
                scraped_listings = scraper.scrape_listings(search_criteria)
            except Exception as e:
                logger.error(f"Scraper.run error: {e}", exc_info=True)
                # Try to close and recreate scraper next run
                try:
                    scraper.close()
                except Exception:
                    pass
                self.scrapers.pop(search_id, None)

            new_count = 0
            updated_count = 0
            below_target_count = 0

            for listing_data in scraped_listings:
                try:
                    if not listing_data:
                        continue
                    platform_id = listing_data.get('platform_id')
                    existing = None
                    if platform_id:
                        existing = db.query(Listing).filter(Listing.platform_id == platform_id).first()

                    # Compute target metric safely
                    target_met = False
                    target_price = getattr(search, 'target_price', None)
                    price_val = listing_data.get('price')
                    if target_price is not None and price_val is not None:
                        try:
                            tp = float(target_price)
                            p = float(price_val)
                            target_met = p <= tp
                        except Exception:
                            target_met = False
                        if target_met:
                            below_target_count += 1

                    if existing:
                        # Update existing listing fields defensively
                        if listing_data.get('price') is not None:
                            existing.price = listing_data.get('price')
                        existing.title = listing_data.get('title') or existing.title
                        existing.description = listing_data.get('description') or existing.description
                        existing.location = listing_data.get('location') or existing.location
                        existing.target_price_met = target_met
                        existing.last_updated = datetime.utcnow()
                        updated_count += 1
                    else:
                        new_listing = Listing(
                            search_id=search_id,
                            platform_id=platform_id,
                            title=listing_data.get('title'),
                            description=listing_data.get('description'),
                            keyword=search.keyword,
                            make=listing_data.get('make'),
                            model=listing_data.get('model'),
                            year=listing_data.get('year'),
                            mileage=listing_data.get('mileage'),
                            price=listing_data.get('price'),
                            fuel_type=listing_data.get('fuel_type'),
                            location=listing_data.get('location'),
                            seller_type=listing_data.get('seller_type', 'Private'),
                            target_price_met=target_met,
                            platform_url=listing_data.get('url'),
                            image_url=listing_data.get('image_url'),
                            power=listing_data.get('power'),
                            seller=listing_data.get('seller')
                        )
                        db.add(new_listing)
                        new_count += 1
                except Exception as e:
                    logger.error(f"Error processing listing data: {e}", exc_info=True)
                    continue

            # Calculate average price over listings with valid numeric prices
            all_listings = db.query(Listing).filter(Listing.search_id == search_id).all()
            prices = []
            for l in all_listings:
                try:
                    if l.price is None:
                        continue
                    p = float(l.price)
                    if p > 0:
                        prices.append(p)
                except Exception as e:
                    logger.debug(f"Invalid price value '{l.price}' for listing {getattr(l, 'id', 'unknown')}: {e}")
                    continue

            if prices:
                avg_price = sum(prices) / len(prices)
                for listing in all_listings:
                    listing.average_price = avg_price

                stat = Statistics(
                    date=datetime.utcnow(),
                    make=search.make,
                    model=search.model,
                    average_price=avg_price,
                    count=len(prices)
                )
                db.add(stat)

            search.last_search_date = datetime.utcnow()
            db.commit()

            # Log success
            success_details = {
                'new_listings': new_count,
                'updated_listings': updated_count,
                'below_target': below_target_count,
                'total_scraped': len(scraped_listings)
            }
            success_log = Log(
                level='success',
                message=f"Scraping completed for {search.name}",
                search_name=search.name,
                details=json.dumps(success_details)
            )
            db.add(success_log)
            db.commit()
            logger.info(f"Scraping completed: {new_count} new, {updated_count} updated, {below_target_count} below target")

            # Send notification email if user wants it
            user_settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            if user_settings and getattr(user_settings, "email", None):
                subject = f"Scraping results for {search.name}"
                body = (
                    f"Scraping completed for search: {search.name}\n\n"
                    f"New listings: {new_count}\n"
                    f"Updated listings: {updated_count}\n"
                    f"Below target: {below_target_count}\n"
                    f"Total scraped: {len(scraped_listings)}\n\n"
                    f"Search URL: {search.site_url}"
                )
                # optional HTML summary
                html = f"""
                <html>
                <body>
                    <h2>Scraping results for {search.name}</h2>
                    <ul>
                        <li>New listings: {new_count}</li>
                        <li>Updated listings: {updated_count}</li>
                        <li>Below target: {below_target_count}</li>
                        <li>Total scraped: {len(scraped_listings)}</li>
                    </ul>
                    <p>Search URL: <a href="{search.site_url}">{search.site_url}</a></p>
                </body>
                </html>
                """
                self._send_gmail_notification(user_settings.email, subject, body, html)

        except Exception as e:
            logger.error(f"Error in scraping: {e}", exc_info=True)
            error_log = Log(
                level='error',
                message=f"Scraping failed: {str(e)}",
                search_name=search.name if search else 'Unknown',
                details=str(e)
            )
            try:
                db.add(error_log)
                db.commit()
            except Exception:
                logger.error("Failed to write error log to DB")
        finally:
            db.close()

