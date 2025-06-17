#!/usr/bin/env python3
"""
Test script to check AXS ticket prices for a specific event
"""

from scrapers.axs_scraper import AXSScraper
import json
import sys

def main():
    # The URL you provided
    url = "https://tix.axs.com/AQAAAAAAAADdMPEOBQAAAAA9%2Fv%2F%2F%2FwD%2F%2F%2F%2F%2FB3JvY2tldHMA%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8=/shop/search"
    
    print("🎫 AXS Ticket Scraper Test")
    print("=" * 50)
    print(f"URL: {url}")
    print("=" * 50)
    
    scraper = AXSScraper()
    
    try:
        print("\n🔍 Fetching ticket information...")
        ticket_data = scraper.get_ticket_info(url)
        
        # Display event info
        if ticket_data.get('event_info'):
            print(f"\n📅 Event: {ticket_data['event_info'].get('name', 'Unknown')}")
            print(f"📆 Date: {ticket_data['event_info'].get('date', 'TBD')}")
        
        # Display price range
        if ticket_data.get('price_range'):
            price_range = ticket_data['price_range']
            if price_range['min'] and price_range['max']:
                print(f"\n💰 Price Range: ${price_range['min']:.2f} - ${price_range['max']:.2f}")
        
        # Display available tickets
        if ticket_data.get('tickets'):
            print(f"\n🎟️  Found {len(ticket_data['tickets'])} ticket options:\n")
            
            for i, ticket in enumerate(ticket_data['tickets'], 1):
                print(f"{i}. Section: {ticket.get('section', 'General')}")
                if ticket.get('row'):
                    print(f"   Row: {ticket['row']}")
                print(f"   Price: ${ticket['price']:.2f}")
                print(f"   Available: {'Yes' if ticket['available'] else 'No'}")
                if ticket.get('fees_included'):
                    print("   Note: Fees may be included")
                print()
        else:
            print(f"\n❌ {ticket_data.get('status', 'No tickets found')}")
        
        # Option to monitor prices
        if ticket_data.get('tickets'):
            monitor = input("\n🔔 Would you like to monitor this event for price drops? (y/n): ")
            if monitor.lower() == 'y':
                interval = input("Check interval in minutes (default 5): ") or "5"
                interval_seconds = int(interval) * 60
                print(f"\n👀 Starting price monitoring (checking every {interval} minutes)...")
                print("Press Ctrl+C to stop\n")
                scraper.monitor_prices(url, interval_seconds)
                
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        scraper.close()
        print("\n✅ Done!")

if __name__ == "__main__":
    main()