"""
Minimal API for Railway deployment - no Chrome dependencies
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

app = FastAPI(title="Toyota Center Ticket Tracker API", version="1.0.0")

# Add CORS middleware
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

@app.get("/")
async def root():
    # Serve dashboard if it exists
    if os.path.exists("dashboard/index.html"):
        return FileResponse("dashboard/index.html")
    return {"message": "Toyota Center Ticket Tracker API", "version": "1.0.0", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/events")
async def get_events():
    """Mock endpoint for testing"""
    return [
        {"name": "Shakira - Las Mujeres Ya No Lloran World Tour", "date": "June 17, 2025", "url": "#"},
        {"name": "Houston Rockets vs Lakers", "date": "TBD", "url": "#"}
    ]

@app.get("/price-drops")
async def get_price_drops(hours: int = 24):
    """Mock endpoint for testing"""
    return []

@app.post("/axs/check")
async def check_axs_event(url: str):
    """Mock endpoint - Chrome not available in basic deployment"""
    return {
        "message": "Chrome-based scraping not available in this deployment",
        "suggestion": "Use the local version or upgrade deployment for full functionality",
        "url": url
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting API on port {port}...")
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"Failed to start: {e}")
        # Fallback to basic HTTP server
        from http.server import HTTPServer, SimpleHTTPRequestHandler
        print(f"Starting fallback server on port {port}...")
        server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
        server.serve_forever()