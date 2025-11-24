"""
Instagram Post Likers Scraper - Extract users who liked posts
Gets username list from post likes, then visits profiles for complete data
Requires: pip install selenium webdriver-manager
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import csv
import re
from datetime import datetime
import json

class InstagramLikersScraper:
    def __init__(self, headless=False):
        """Initialize the scraper with Chrome driver"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.wait = WebDriverWait(self.driver, 20)
        
    def login(self, username, password):
        """Login to Instagram"""
        try:
            print("Opening Instagram...")
            self.driver.get("https://www.instagram.com/")
            time.sleep(3)
            
            try:
                cookie_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Allow') or contains(text(), 'Accept')]")
                cookie_button.click()
                time.sleep(1)
            except:
                pass
            
            print("Logging in...")
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.send_keys(username)
            
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.send_keys(password)
            
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            time.sleep(5)
            
            try:
                not_now = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Not now') or contains(text(), 'Not Now')]")
                not_now.click()
                time.sleep(2)
            except:
                pass
            
            try:
                not_now = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now') or contains(text(), 'Not now')]")
                not_now.click()
                time.sleep(2)
            except:
                pass
            
            print("✓ Login successful!\n")
            return True
            
        except Exception as e:
            print(f"✗ Login failed: {e}")
            return False
    
    def get_post_links_from_profile(self, profile_url, max_posts=1000):
    
        try:
            print(f"{'='*60}")
            print(f"Opening Profile")
            print(f"{'='*60}")
            print(f"URL: {profile_url}\n")

            self.driver.get(profile_url)
            time.sleep(5)

            print("Waiting for posts to load...")
            time.sleep(3)

            post_links = set()
            previous_height = 0
            scroll_attempts = 0

            print(f"Scrolling to collect posts (target: {max_posts} posts)...")
            print("-" * 60)

            while len(post_links) < max_posts:
                # find all visible post links
                post_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
                for elem in post_elements:
                    href = elem.get_attribute('href')
                    if href and '/p/' in href:
                        post_links.add(href)
                        if len(post_links) >= max_posts:
                            break

                print(f"Collected {len(post_links)} post links so far...", end="\r")

                # scroll down to load more posts
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

                # check if scrolled to bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == previous_height:
                    scroll_attempts += 1
                    if scroll_attempts >= 3:
                        print("\n✓ Reached end of page (no more posts)")
                        break
                else:
                    scroll_attempts = 0

                previous_height = new_height

            post_links = list(post_links)
            print(f"\n✓ Found {len(post_links)} post links total\n")
            return post_links[:max_posts]

        except Exception as e:
            print(f"✗ Error getting post links: {e}")
            import traceback
            traceback.print_exc()
            return []

  
  
  
    def get_likers_from_post_url(self, post_url, max_likers=50):
        """Open a specific post URL and get likers"""
        try:
            print(f"Opening post: {post_url}")
            self.driver.get(post_url)
            time.sleep(5)
            
            print("Looking for likes button...")
            
            likes_button = None
            likes_count = "unknown"
            
            # Try multiple methods to find the likes button
            try:
                # Method 1: Direct link with /liked_by/
                likes_button = self.driver.find_element(By.XPATH, "//a[contains(@href, '/liked_by/')]")
                likes_count = likes_button.text
                print(f"✓ Found: {likes_count}")
            except:
                try:
                    # Method 2: Section with likes text
                    likes_elements = self.driver.find_elements(By.XPATH, "//section//span[contains(text(), 'like')]")
                    for elem in likes_elements:
                        if 'like' in elem.text.lower():
                            likes_button = elem
                            likes_count = elem.text
                            print(f"✓ Found: {likes_count}")
                            break
                except:
                    pass
                
                if not likes_button:
                    try:
                        # Method 3: Button with likes
                        likes_elements = self.driver.find_elements(By.XPATH, "//button//span[contains(text(), 'like')]")
                        for elem in likes_elements:
                            if 'like' in elem.text.lower() and any(char.isdigit() for char in elem.text):
                                likes_button = elem
                                likes_count = elem.text
                                print(f"✓ Found: {likes_count}")
                                break
                    except:
                        pass
                
                if not likes_button:
                    try:
                        # Method 4: Any span with "likes" text
                        likes_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'likes') or contains(text(), 'like')]")
                        for elem in likes_elements:
                            text = elem.text
                            if any(char.isdigit() for char in text) and 'like' in text.lower():
                                likes_button = elem
                                likes_count = text
                                print(f"✓ Found: {likes_count}")
                                break
                    except:
                        pass
            
            if not likes_button:
                print("✗ Could not find likes button. Post may have likes hidden or no likes.")
                return []
            
            print(f"Clicking likes button: {likes_count}...")
            try:
                likes_button.click()
            except:
                try:
                    self.driver.execute_script("arguments[0].click();", likes_button)
                except:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", likes_button)
                    time.sleep(1)
                    likes_button.click()
            
            time.sleep(4)
            
            print("Waiting for likes dialog...")
            likes_dialog = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            
            print(f"Collecting usernames (target: {max_likers})...")
            print("-" * 60)
            
            liker_usernames = set()
            last_count = 0
            no_change_count = 0
            
            while len(liker_usernames) < max_likers:
                user_links = self.driver.find_elements(By.XPATH, "//div[@role='dialog']//a[contains(@href, '/')]")
                
                for link in user_links:
                    try:
                        href = link.get_attribute('href')
                        if href and '/accounts/' not in href and href != 'https://www.instagram.com/':
                            username = href.rstrip('/').split('/')[-1]
                            # Filter out invalid usernames
                            if (username and 
                                not username.startswith('explore') and 
                                username not in ['liked_by', 'repost'] and
                                '%' not in username and
                                username not in liker_usernames):
                                liker_usernames.add(username)
                                print(f"  [{len(liker_usernames)}] @{username}")
                    except:
                        continue
                
                if len(liker_usernames) >= max_likers:
                    print(f"\n✓ Reached target: {max_likers} usernames")
                    break
                
                if len(liker_usernames) == last_count:
                    no_change_count += 1
                    if no_change_count >= 3:
                        print(f"\n✓ Reached end of likes list ({len(liker_usernames)} total)")
                        break
                else:
                    no_change_count = 0
                    last_count = len(liker_usernames)
                
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight", 
                    likes_dialog
                )
                time.sleep(2)
            
            print("\nClosing likes dialog...")
            try:
                close_button = self.driver.find_element(By.XPATH, "//div[@role='dialog']//button")
                close_button.click()
            except:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            
            time.sleep(1)
            
            return list(liker_usernames)[:max_likers]
            
        except Exception as e:
            print(f"✗ Error getting likers: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def scrape_profile_details(self, username):
        """Visit individual profile and scrape complete data"""
        try:
            profile_url = f"https://www.instagram.com/{username}/"
            self.driver.get(profile_url)
            time.sleep(7)
            
            profile_data = {
                'username': username,
                'full_name': '',
                'bio': '',
                'email': '',
                'phone': '',
                'followers': '',
                'following': '',
                'posts': '',
                'profile_url': profile_url,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            try:
                full_name = self.driver.find_element(By.XPATH, "//span[contains(@class, 'x1lliihq')]").text
                profile_data['full_name'] = full_name
            except:
                try:
                    full_name = self.driver.find_element(By.XPATH, "//section//div//span").text
                    profile_data['full_name'] = full_name
                except:
                    pass
            
            try:
                bio_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, '_ap3a')]//span")
                if not bio_elements:
                    bio_elements = self.driver.find_elements(By.XPATH, "//section//div//span[contains(@class, '_ap3a')]")
                
                bio_text = ' '.join([el.text for el in bio_elements if el.text])
                profile_data['bio'] = bio_text
                
                email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                email_match = re.search(email_pattern, bio_text)
                if email_match:
                    profile_data['email'] = email_match.group(0)
                
                phone_pattern = r'[\+\(]?[1-9][0-9\s\-\(\)\.]{7,}[0-9]'
                phone_match = re.search(phone_pattern, bio_text)
                if phone_match:
                    profile_data['phone'] = phone_match.group(0).strip()
            except:
                pass
            
            try:
                stats = self.driver.find_elements(By.XPATH, "//ul//li//span[@class='html-span xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1hl2dhg x16tdsg8 x1vvkbs']")
                
                if len(stats) >= 3:
                    profile_data['posts'] = stats[0].get_attribute('title') or stats[0].text
                    profile_data['followers'] = stats[1].get_attribute('title') or stats[1].text
                    profile_data['following'] = stats[2].get_attribute('title') or stats[2].text
                else:
                    stats_alt = self.driver.find_elements(By.XPATH, "//ul//li//span//span")
                    if len(stats_alt) >= 3:
                        profile_data['posts'] = stats_alt[0].text
                        profile_data['followers'] = stats_alt[1].text
                        profile_data['following'] = stats_alt[2].text
            except:
                pass
            
            try:
                contact_button = self.driver.find_element(By.XPATH, "//a[contains(@href, 'mailto:')]")
                email_href = contact_button.get_attribute('href')
                if 'mailto:' in email_href:
                    profile_data['email'] = email_href.replace('mailto:', '').split('?')[0]
            except:
                pass
            
            return profile_data
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
            return None
    
    def scrape_likers_complete(self, target_profile_url, max_posts=3, max_likers_per_post=50, delay=3):
        """Main function: Complete workflow"""
        print(f"\n{'='*60}")
        print(f"INSTAGRAM POST LIKERS SCRAPER")
        print(f"{'='*60}")
        print(f"Target: {target_profile_url}")
        print(f"Max posts: {max_posts}")
        print(f"Max likers per post: {max_likers_per_post}")
        print(f"{'='*60}\n")
        
        # Step 1: Get post links from profile
        post_links = self.get_post_links_from_profile(target_profile_url, max_posts)
        
        if not post_links:
            print("\n✗ No posts found!")
            return []
        
        # Step 2: Get likers from each post
        all_likers = set()
        
        for idx, post_url in enumerate(post_links, 1):
            print(f"\n{'='*60}")
            print(f"POST {idx}/{len(post_links)}")
            print(f"{'='*60}\n")
            
            likers = self.get_likers_from_post_url(post_url, max_likers_per_post)
            
            if likers:
                all_likers.update(likers)
                print(f"\n✓ Got {len(likers)} likers from this post")
                print(f"✓ Total unique likers so far: {len(all_likers)}")
            else:
                print("\n✗ No likers found for this post")
            
            time.sleep(2)
        
        all_likers_list = list(all_likers)
        
        if not all_likers_list:
            print("\n✗ No likers found!")
            return []
        
        # Step 3: Scrape each liker's profile
        print(f"\n{'='*60}")
        print(f"SCRAPING PROFILE DETAILS")
        print(f"{'='*60}")
        print(f"Visiting {len(all_likers_list)} profiles for complete data...\n")
        
        all_profiles_data = []
        
        for idx, username in enumerate(all_likers_list, 1):
            print(f"[{idx}/{len(all_likers_list)}] @{username:<20}", end=" ")
            
            profile_data = self.scrape_profile_details(username)
            
            if profile_data:
                all_profiles_data.append(profile_data)
                print(f"| {profile_data['full_name']:<25} | 📧 {profile_data['email'] or 'N/A':<25} | 👥 {profile_data['followers']}")
            else:
                print(f"| Failed to scrape")
            
            if idx < len(all_likers_list):
                time.sleep(delay)
        
        print(f"\n{'='*60}")
        print(f"✓ Successfully scraped {len(all_profiles_data)}/{len(all_likers_list)} profiles")
        print(f"{'='*60}\n")
        
        return all_profiles_data
    
    def save_to_csv(self, data, filename='likers_data.csv'):
        """Save scraped data to CSV file"""
        if not data:
            print("No data to save")
            return
        
        try:
            fieldnames = ['username', 'full_name', 'bio', 'email', 'phone', 
                         'followers', 'following', 'posts', 'profile_url', 'scraped_at']
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(data)
            
            print(f"✓ CSV saved: {filename} (UTF-8 encoding)")
            print(f"  Note: Open with Excel or use 'Import Data' feature for proper character display")
        except Exception as e:
            print(f"✗ Error saving to CSV: {e}")
    
    def save_to_json(self, data, filename='likers_data.json'):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ JSON saved: {filename}")
        except Exception as e:
            print(f"✗ Error saving to JSON: {e}")
    
    def close(self):
        """Close the browser"""
        self.driver.quit()
        print("\n✓ Browser closed.")


if __name__ == "__main__":
    
    INSTAGRAM_USERNAME = "carloslennix38@gmail.com"
    INSTAGRAM_PASSWORD = "whitepig527@"
    
    TARGET_PROFILE = "https://www.instagram.com/bostonmedical.oficial"
    
    MAX_POSTS = 40  # Increased to get more posts
    MAX_LIKERS_PER_POST = 100  # Increased to get more likers
    DELAY_BETWEEN_PROFILES = 3
    
    scraper = InstagramLikersScraper(headless=False)
    
    try:
        if scraper.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD):
            
            likers_data = scraper.scrape_likers_complete(
                target_profile_url=TARGET_PROFILE,
                max_posts=MAX_POSTS,
                max_likers_per_post=MAX_LIKERS_PER_POST,
                delay=DELAY_BETWEEN_PROFILES
            )
            
            if likers_data:
                print("="*60)
                print("FINAL SUMMARY")
                print("="*60)
                print(f"Total profiles: {len(likers_data)}")
                
                emails_found = sum(1 for p in likers_data if p['email'])
                phones_found = sum(1 for p in likers_data if p['phone'])
                bios_found = sum(1 for p in likers_data if p['bio'])
                
                print(f"✓ Emails found: {emails_found}")
                print(f"✓ Phone numbers found: {phones_found}")
                print(f"✓ Bios found: {bios_found}")
                print("="*60 + "\n")
                
                scraper.save_to_csv(likers_data)
                scraper.save_to_json(likers_data)
                
                print("\n" + "-"*60)
                print("SAMPLE DATA (First 3 profiles):")
                print("-"*60)
                for profile in likers_data[:3]:
                    print(f"\n@{profile['username']}")
                    print(f"  Name: {profile['full_name']}")
                    print(f"  Bio: {profile['bio'][:80] + '...' if len(profile['bio']) > 80 else profile['bio']}")
                    print(f"  Email: {profile['email'] or 'N/A'}")
                    print(f"  Phone: {profile['phone'] or 'N/A'}")
                    print(f"  Stats: {profile['posts']} posts | {profile['followers']} followers | {profile['following']} following")
            else:
                print("✗ No data collected")
            
        else:
            print("\n✗ Cannot proceed without login.")
    
    except KeyboardInterrupt:
        print("\n\n⚠ Scraping interrupted by user.")
    except Exception as e:
        print(f"\n✗ An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        time.sleep(3)
        scraper.close()
    
    print("\n" + "="*60)
    print("DONE!")
    print("="*60 + "\n")