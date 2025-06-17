from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import sys
sys.path.append('..')

from scrapers.toyota_center_scraper import ToyotaCenterScraper
from models.database import SessionLocal, Event, TicketPrice, PriceDrop
from datetime import datetime

scheduler = BackgroundScheduler()
scraper = ToyotaCenterScraper()

def check_all_events():
    """Check all events for price changes"""
    try:
        db = SessionLocal()
        events = db.query(Event).all()
        
        for event in events:
            current_prices = scraper.get_ticket_prices(event.url)
            
            for ticket in current_prices:
                last_price = db.query(TicketPrice).filter(
                    TicketPrice.event_id == event.id,
                    TicketPrice.section == ticket['section']
                ).order_by(TicketPrice.tracked_at.desc()).first()
                
                if last_price and ticket['price'] < last_price.price:
                    drop_percentage = ((last_price.price - ticket['price']) / last_price.price) * 100
                    
                    price_drop = PriceDrop(
                        event_id=event.id,
                        section=ticket['section'],
                        old_price=last_price.price,
                        new_price=ticket['price'],
                        drop_percentage=drop_percentage
                    )
                    db.add(price_drop)
                    
                    print(f"Price drop detected! {event.event_name} - {ticket['section']}: "
                          f"${last_price.price} -> ${ticket['price']} ({drop_percentage:.1f}% off)")
                
                new_price = TicketPrice(
                    event_id=event.id,
                    section=ticket['section'],
                    price=ticket['price'],
                    availability=ticket['available'],
                    source=ticket['source']
                )
                db.add(new_price)
        
        db.commit()
        db.close()
    except Exception as e:
        print(f"Error in scheduled check: {e}")

def start_monitoring():
    """Start the background scheduler"""
    scheduler.add_job(
        check_all_events,
        trigger=IntervalTrigger(minutes=30),
        id='check_prices',
        name='Check all event prices',
        replace_existing=True
    )
    scheduler.start()
    print("Price monitoring scheduler started - checking every 30 minutes")

def stop_monitoring():
    """Stop the background scheduler"""
    scheduler.shutdown()
    print("Price monitoring scheduler stopped")