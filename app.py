"""Ultra-minimal FastAPI app for Railway"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Toyota Center Ticket Tracker</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 40px; text-align: center; }
            h1 { color: #333; }
            .status { color: green; }
            .info { margin: 20px 0; padding: 20px; background: #f0f0f0; border-radius: 8px; }
        </style>
    </head>
    <body>
        <h1>🎫 Toyota Center Ticket Tracker</h1>
        <p class="status">✅ API is running!</p>
        <div class="info">
            <p>This is a minimal deployment on Railway.</p>
            <p>For full functionality (web scraping), please run locally.</p>
            <p><a href="/docs">API Documentation</a></p>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)