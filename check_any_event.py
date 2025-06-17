#!/usr/bin/env python3
"""
Check ticket prices for any Toyota Center event
"""

import sys
from scrapers.axs_scraper import AXSScraper
import time
from datetime import datetime

def check_event(url):
    """Check ticket prices for any event URL"""
    print("🎫 Checking ticket prices...")
    print("=" * 60)
    
    scraper = AXSScraper()
    
    try:
        print("🔍 Loading page (this may take 10-20 seconds)...")
        data = scraper.get_ticket_info(url)
        
        if data.get('event_info'):
            print(f"\n📅 Event: {data['event_info'].get('name', 'Unknown Event')}")
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
            
            return data
        else:
            print(f"\n❌ {data.get('status', 'No tickets found')}")
            print("\nThis could mean:")
            print("- Event is sold out")
            print("- Tickets not on sale yet")
            print("- Page layout has changed")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        scraper.close()

def main():
    print("🎭 TOYOTA CENTER EVENT TICKET CHECKER")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # URL provided as command line argument
        url = sys.argv[1]
    else:
        # Ask for URL
        print("\nEnter the event URL from AXS or Toyota Center")
        print("(or press Enter to check Shakira tickets)")
        url = input("\nURL: ").strip()
        
        if not url:
            # Default to Shakira if no URL provided
            print("\n🎤 Checking Shakira - Las Mujeres Ya No Lloran World Tour...")
            url = "https://www.toyotacenter.com/events/detail/shakira-2025"
    
    check_event(url)
    
    # Ask if they want to monitor
    monitor = input("\n\n🔔 Monitor this event for price drops? (y/n): ")
    if monitor.lower() == 'y':
        interval = input("Check every how many minutes? (default 5): ").strip() or "5"
        interval_seconds = int(interval) * 60
        
        print(f"\n👀 Monitoring every {interval} minutes...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                time.sleep(interval_seconds)
                print(f"\n{'='*60}")
                print(f"⏰ Checking at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*60)
                check_event(url)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped")

if __name__ == "__main__":
    main()