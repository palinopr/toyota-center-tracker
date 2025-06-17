#!/usr/bin/env python3
"""
Start the ticket tracker dashboard
"""

import subprocess
import webbrowser
import time
import os
import sys
from pathlib import Path

def start_services():
    print("🚀 Starting Toyota Center Ticket Tracker Dashboard")
    print("=" * 50)
    
    # Check if API is already running
    api_running = False
    try:
        import requests
        response = requests.get("http://localhost:8000")
        if response.status_code == 200:
            api_running = True
            print("✅ API is already running")
    except:
        pass
    
    # Start API if not running
    api_process = None
    if not api_running:
        print("📡 Starting API server...")
        api_process = subprocess.Popen(
            [sys.executable, "api/main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for API to start
        print("⏳ Waiting for API to start...")
        for i in range(10):
            try:
                import requests
                response = requests.get("http://localhost:8000")
                if response.status_code == 200:
                    print("✅ API started successfully")
                    break
            except:
                time.sleep(1)
    
    # Start simple HTTP server for dashboard
    print("🌐 Starting dashboard server...")
    dashboard_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8080", "--directory", "dashboard"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Open dashboard in browser
    time.sleep(2)
    dashboard_url = "http://localhost:8080"
    print(f"\n✨ Dashboard is ready at: {dashboard_url}")
    print("\n📋 Quick Start Guide:")
    print("1. Click 'Check Event URL' to add an event")
    print("2. Paste any AXS or Toyota Center event URL")
    print("3. Watch real-time price updates and drops")
    print("\n🛑 Press Ctrl+C to stop all services")
    
    # Open browser
    webbrowser.open(dashboard_url)
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down services...")
        if api_process:
            api_process.terminate()
        dashboard_process.terminate()
        print("✅ All services stopped")

if __name__ == "__main__":
    # Make sure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check for required packages
    try:
        import requests
    except ImportError:
        print("⚠️  Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    
    start_services()