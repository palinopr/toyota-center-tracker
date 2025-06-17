#!/usr/bin/env python3
"""
Simple script to check Rockets ticket prices
"""

import requests
import json
import subprocess
import time
import sys

# The Rockets game URL
ROCKETS_URL = "https://tix.axs.com/AQAAAAAAAADdMPEOBQAAAAA9%2Fv%2F%2F%2FwD%2F%2F%2F%2F%2FB3JvY2tldHMA%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8=/shop/search"

def check_with_scraper():
    """Use the direct scraper to check prices"""
    print("🏀 Checking Rockets ticket prices directly...")
    print("=" * 60)
    
    try:
        from scrapers.axs_scraper import AXSScraper
        
        scraper = AXSScraper()
        print("🔍 Fetching ticket data (this may take 10-20 seconds)...")
        
        data = scraper.get_ticket_info(ROCKETS_URL)
        
        if data.get('event_info'):
            print(f"\n📅 Event: {data['event_info'].get('name', 'Rockets Game')}")
            print(f"📆 Date: {data['event_info'].get('date', 'Check website')}")
        
        if data.get('tickets'):
            print(f"\n💰 Found {len(data['tickets'])} ticket options:")
            print("-" * 60)
            
            # Sort by price
            sorted_tickets = sorted(data['tickets'], key=lambda x: x['price'])
            
            for ticket in sorted_tickets:
                print(f"Section: {ticket.get('section', 'General'):15} | Price: ${ticket['price']:>8.2f}", end="")
                if ticket.get('row'):
                    print(f" | Row: {ticket['row']}", end="")
                print(f" | {'Available' if ticket['available'] else 'Sold Out'}")
            
            print("-" * 60)
            print(f"Price Range: ${min(t['price'] for t in data['tickets']):.2f} - ${max(t['price'] for t in data['tickets']):.2f}")
        else:
            print(f"\n❌ {data.get('status', 'No tickets found')}")
            
        scraper.close()
        return data
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

def check_with_api():
    """Use the API to check prices"""
    print("\n\n🖥️  Checking via API...")
    print("=" * 60)
    
    try:
        response = requests.post(
            "http://localhost:8000/axs/check",
            json={"url": ROCKETS_URL},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API check successful!")
            return data
        else:
            print(f"❌ API error: {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ API not running. Start it with: cd api && python main.py")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🏀 HOUSTON ROCKETS TICKET CHECKER")
    print("=" * 60)
    print("Choose an option:")
    print("1. Quick check (direct scraper)")
    print("2. API check (requires API running)")
    print("3. Monitor prices (check every 5 minutes)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        check_with_scraper()
        
    elif choice == "2":
        check_with_api()
        
    elif choice == "3":
        print("\n👀 Starting price monitoring...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                data = check_with_scraper()
                print(f"\n⏰ Last checked: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("Waiting 5 minutes for next check...")
                time.sleep(300)  # 5 minutes
                print("\n" + "="*60 + "\n")
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped")
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()