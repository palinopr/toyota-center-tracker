from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
import os
sys.path.append('..')

from scrapers.toyota_center_scraper import ToyotaCenterScraper
from scrapers.axs_scraper import AXSScraper
from models.database import SessionLocal, Event, TicketPrice, PriceDrop
from utils.scheduler import start_monitoring
import json

app = FastAPI(title="Toyota Center Ticket Tracker API", version="1.0.0")

# Add CORS middleware for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for dashboard
if os.path.exists("dashboard"):
    app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")

scraper = ToyotaCenterScraper()
axs_scraper = AXSScraper()

class EventResponse(BaseModel):
    name: str
    date: str
    url: str
    
class TicketResponse(BaseModel):
    section: str
    price: float
    available: bool
    source: str
    
class PriceDropResponse(BaseModel):
    event: str
    section: str
    old_price: float
    new_price: float
    drop_percentage: float
    detected_at: datetime

@app.on_event("startup")
async def startup_event():
    """Initialize background monitoring on startup"""
    start_monitoring()

@app.get("/")
async def root():
    # Redirect to dashboard if it exists
    if os.path.exists("dashboard/index.html"):
        return FileResponse("dashboard/index.html")
    return {"message": "Toyota Center Ticket Tracker API", "version": "1.0.0"}

@app.get("/events", response_model=List[EventResponse])
async def get_events():
    """Get all upcoming events at Toyota Center"""
    try:
        events = scraper.get_upcoming_events()
        
        db = SessionLocal()
        for event in events:
            existing = db.query(Event).filter(Event.event_name == event['name']).first()
            if not existing:
                db_event = Event(
                    event_name=event['name'],
                    event_date=datetime.now(),
                    url=event['url']
                )
                db.add(db_event)
        db.commit()
        db.close()
        
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/events/{event_name}/tickets", response_model=List[TicketResponse])
async def get_ticket_prices(event_name: str):
    """Get current ticket prices for a specific event"""
    try:
        db = SessionLocal()
        event = db.query(Event).filter(Event.event_name == event_name).first()
        db.close()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        tickets = scraper.get_ticket_prices(event.url)
        
        db = SessionLocal()
        for ticket in tickets:
            db_ticket = TicketPrice(
                event_id=event.id,
                section=ticket['section'],
                price=ticket['price'],
                availability=ticket['available'],
                source=ticket['source']
            )
            db.add(db_ticket)
        db.commit()
        db.close()
        
        return tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/price-drops", response_model=List[PriceDropResponse])
async def get_price_drops(hours: int = 24):
    """Get recent price drops within specified hours"""
    try:
        db = SessionLocal()
        from datetime import timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        drops = db.query(PriceDrop).filter(PriceDrop.detected_at >= cutoff_time).all()
        db.close()
        
        response = []
        for drop in drops:
            db = SessionLocal()
            event = db.query(Event).filter(Event.id == drop.event_id).first()
            db.close()
            
            response.append({
                'event': event.event_name if event else 'Unknown',
                'section': drop.section,
                'old_price': drop.old_price,
                'new_price': drop.new_price,
                'drop_percentage': drop.drop_percentage,
                'detected_at': drop.detected_at
            })
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/monitor/{event_name}")
async def start_monitoring_event(event_name: str, background_tasks: BackgroundTasks):
    """Start monitoring a specific event for price drops"""
    try:
        db = SessionLocal()
        event = db.query(Event).filter(Event.event_name == event_name).first()
        db.close()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        background_tasks.add_task(monitor_event_prices, event)
        
        return {"message": f"Started monitoring {event_name} for price drops"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def monitor_event_prices(event):
    """Background task to monitor event prices"""
    try:
        current_prices = scraper.get_ticket_prices(event.url)
        
        db = SessionLocal()
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
        print(f"Error monitoring prices: {e}")

@app.get("/events/{event_name}/history")
async def get_price_history(event_name: str, section: Optional[str] = None):
    """Get historical price data for an event"""
    try:
        db = SessionLocal()
        event = db.query(Event).filter(Event.event_name == event_name).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        query = db.query(TicketPrice).filter(TicketPrice.event_id == event.id)
        
        if section:
            query = query.filter(TicketPrice.section == section)
        
        history = query.order_by(TicketPrice.tracked_at.desc()).limit(100).all()
        db.close()
        
        return [{
            'section': h.section,
            'price': h.price,
            'available': h.availability,
            'tracked_at': h.tracked_at
        } for h in history]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/axs/check")
async def check_axs_event(url: str):
    """Check ticket prices for an AXS event URL"""
    try:
        ticket_data = axs_scraper.get_ticket_info(url)
        
        # Store event if it has valid data
        if ticket_data.get('event_info') and ticket_data.get('event_info').get('name'):
            db = SessionLocal()
            event_name = ticket_data['event_info']['name']
            
            existing = db.query(Event).filter(Event.event_name == event_name).first()
            if not existing:
                db_event = Event(
                    event_name=event_name,
                    event_date=datetime.now(),  # Parse actual date if available
                    url=url,
                    venue="Toyota Center"
                )
                db.add(db_event)
                db.commit()
                event_id = db_event.id
            else:
                event_id = existing.id
            
            # Store ticket prices
            for ticket in ticket_data.get('tickets', []):
                db_ticket = TicketPrice(
                    event_id=event_id,
                    section=ticket.get('section', 'General'),
                    row=ticket.get('row', ''),
                    price=ticket['price'],
                    availability=ticket['available'],
                    source='AXS'
                )
                db.add(db_ticket)
            
            db.commit()
            db.close()
        
        return ticket_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/axs/monitor/{event_name}")
async def get_axs_monitoring_status(event_name: str):
    """Get the current monitoring status and recent prices for an AXS event"""
    try:
        db = SessionLocal()
        event = db.query(Event).filter(Event.event_name == event_name).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Get last 10 price checks
        recent_prices = db.query(TicketPrice).filter(
            TicketPrice.event_id == event.id,
            TicketPrice.source == 'AXS'
        ).order_by(TicketPrice.tracked_at.desc()).limit(10).all()
        
        db.close()
        
        return {
            "event": event_name,
            "url": event.url,
            "recent_checks": [{
                "section": p.section,
                "row": p.row,
                "price": p.price,
                "available": p.availability,
                "checked_at": p.tracked_at
            } for p in recent_prices]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)