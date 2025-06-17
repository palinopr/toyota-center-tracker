from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
import time
import re
from datetime import datetime
import random

class AXSScraper:
    def __init__(self):
        self.setup_driver()
        
    def setup_driver(self):
        """Setup undetected Chrome driver to bypass AXS anti-bot measures"""
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-accelerated-2d-canvas')
        options.add_argument('--disable-gpu')
        
        # Use undetected-chromedriver to bypass detection
        self.driver = uc.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def get_ticket_info(self, url):
        """Scrape ticket information from AXS event page"""
        try:
            self.driver.get(url)
            
            # Random delay to appear more human
            time.sleep(random.uniform(3, 5))
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, 20)
            
            ticket_data = {
                'event_info': {},
                'tickets': [],
                'price_range': {'min': None, 'max': None}
            }
            
            # Try to get event info
            try:
                event_name = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[class*="event-name"], [class*="event-title"], h1')
                )).text
                ticket_data['event_info']['name'] = event_name
            except:
                ticket_data['event_info']['name'] = "Unknown Event"
            
            # Try to get date/time
            try:
                date_element = self.driver.find_element(
                    By.CSS_SELECTOR, '[class*="event-date"], [class*="date-time"], time'
                )
                ticket_data['event_info']['date'] = date_element.text
            except:
                ticket_data['event_info']['date'] = "Date TBD"
            
            # Scroll to load all sections
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            
            # Look for ticket listings
            ticket_sections = self.driver.find_elements(
                By.CSS_SELECTOR, '[class*="ticket"], [class*="seat"], [class*="listing"], [class*="inventory"]'
            )
            
            prices = []
            
            for section in ticket_sections:
                try:
                    text = section.text
                    
                    # Extract price
                    price_match = re.search(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', text)
                    if price_match:
                        price = float(price_match.group(1).replace(',', ''))
                        prices.append(price)
                        
                        # Extract section info
                        section_info = {
                            'price': price,
                            'section': 'General',
                            'available': 'sold out' not in text.lower(),
                            'fees_included': 'fees' in text.lower()
                        }
                        
                        # Try to extract section name
                        section_match = re.search(r'(?:section|sec|level)\s*(\w+)', text, re.IGNORECASE)
                        if section_match:
                            section_info['section'] = section_match.group(1)
                        
                        # Check for row info
                        row_match = re.search(r'(?:row|rw)\s*(\w+)', text, re.IGNORECASE)
                        if row_match:
                            section_info['row'] = row_match.group(1)
                        
                        ticket_data['tickets'].append(section_info)
                except Exception as e:
                    continue
            
            # Calculate price range
            if prices:
                ticket_data['price_range']['min'] = min(prices)
                ticket_data['price_range']['max'] = max(prices)
            
            # Check if tickets are available
            if not ticket_data['tickets']:
                # Look for "no tickets available" message
                no_tickets = self.driver.find_elements(
                    By.CSS_SELECTOR, '[class*="no-ticket"], [class*="sold-out"], [class*="unavailable"]'
                )
                if no_tickets:
                    ticket_data['status'] = "Sold Out or No Tickets Available"
                else:
                    ticket_data['status'] = "Tickets may be available - check manually"
            else:
                ticket_data['status'] = f"Found {len(ticket_data['tickets'])} ticket options"
            
            return ticket_data
            
        except Exception as e:
            print(f"Error scraping AXS: {e}")
            return {
                'error': str(e),
                'event_info': {},
                'tickets': [],
                'status': 'Error accessing ticket page'
            }
    
    def monitor_prices(self, url, check_interval=300):
        """Monitor ticket prices for changes"""
        previous_prices = {}
        
        while True:
            current_data = self.get_ticket_info(url)
            
            if current_data.get('tickets'):
                for ticket in current_data['tickets']:
                    key = f"{ticket.get('section', 'General')}_{ticket.get('row', 'Any')}"
                    current_price = ticket['price']
                    
                    if key in previous_prices:
                        if current_price < previous_prices[key]:
                            drop = previous_prices[key] - current_price
                            drop_pct = (drop / previous_prices[key]) * 100
                            
                            print(f"🎉 PRICE DROP DETECTED!")
                            print(f"Section: {ticket.get('section', 'General')}")
                            print(f"Previous: ${previous_prices[key]:.2f}")
                            print(f"Current: ${current_price:.2f}")
                            print(f"Savings: ${drop:.2f} ({drop_pct:.1f}% off)")
                            print("-" * 40)
                    
                    previous_prices[key] = current_price
            
            print(f"Checked at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Next check in {check_interval} seconds...")
            time.sleep(check_interval)
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()