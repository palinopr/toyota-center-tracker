import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import time
from datetime import datetime
import re

class ToyotaCenterScraper:
    def __init__(self):
        self.base_url = "https://www.toyotacenter.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def get_upcoming_events(self):
        """Scrape upcoming events from Toyota Center website"""
        try:
            response = requests.get(f"{self.base_url}/events", headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            events = []
            event_elements = soup.find_all('div', class_='event-item') or soup.find_all('article', class_='event')
            
            for event in event_elements:
                event_data = {
                    'name': event.find('h3', class_='event-title') or event.find('h2'),
                    'date': event.find('time') or event.find('span', class_='date'),
                    'url': event.find('a', href=True)
                }
                
                if event_data['name'] and event_data['url']:
                    events.append({
                        'name': event_data['name'].text.strip(),
                        'date': event_data['date'].text.strip() if event_data['date'] else 'TBD',
                        'url': event_data['url']['href'] if not event_data['url']['href'].startswith('http') 
                               else event_data['url']['href']
                    })
            
            return events
        except Exception as e:
            print(f"Error scraping events: {e}")
            return []
    
    def get_ticket_prices(self, event_url):
        """Get ticket prices for a specific event using Selenium"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            driver.get(event_url)
            time.sleep(3)
            
            ticket_data = []
            
            price_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="price"], [class*="ticket"]')
            
            for element in price_elements:
                text = element.text
                price_match = re.search(r'\$(\d+(?:\.\d{2})?)', text)
                
                if price_match:
                    price = float(price_match.group(1))
                    section = "General"
                    
                    parent = element.find_element(By.XPATH, '..')
                    section_text = parent.text
                    
                    if 'section' in section_text.lower():
                        section_match = re.search(r'section\s*(\w+)', section_text, re.IGNORECASE)
                        if section_match:
                            section = section_match.group(1)
                    
                    ticket_data.append({
                        'section': section,
                        'price': price,
                        'available': 'sold out' not in text.lower(),
                        'source': 'Toyota Center'
                    })
            
            return ticket_data
            
        except Exception as e:
            print(f"Error getting ticket prices: {e}")
            return []
        finally:
            driver.quit()
    
    def monitor_price_drops(self, events_to_monitor):
        """Monitor multiple events for price drops"""
        price_drops = []
        
        for event in events_to_monitor:
            current_prices = self.get_ticket_prices(event['url'])
            
            for ticket in current_prices:
                historical_price = self.get_historical_price(event['name'], ticket['section'])
                
                if historical_price and ticket['price'] < historical_price:
                    drop_percentage = ((historical_price - ticket['price']) / historical_price) * 100
                    
                    price_drops.append({
                        'event': event['name'],
                        'section': ticket['section'],
                        'old_price': historical_price,
                        'new_price': ticket['price'],
                        'drop_percentage': round(drop_percentage, 2),
                        'detected_at': datetime.now()
                    })
        
        return price_drops
    
    def get_historical_price(self, event_name, section):
        """Mock function to get historical price - should query database"""
        return None