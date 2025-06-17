from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./toyota_center_tickets.db")

# Handle Railway PostgreSQL URL format
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String, index=True)
    event_date = Column(DateTime)
    venue = Column(String, default="Toyota Center")
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TicketPrice(Base):
    __tablename__ = "ticket_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, index=True)
    section = Column(String)
    row = Column(String, nullable=True)
    price = Column(Float)
    availability = Column(Boolean, default=True)
    source = Column(String)
    tracked_at = Column(DateTime, default=datetime.utcnow)
    
class PriceDrop(Base):
    __tablename__ = "price_drops"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, index=True)
    section = Column(String)
    old_price = Column(Float)
    new_price = Column(Float)
    drop_percentage = Column(Float)
    detected_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)