#!/bin/bash

echo "🎫 Toyota Center Ticket Checker - Quick Start"
echo "============================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -q selenium undetected-chromedriver beautifulsoup4 requests

echo ""
echo "✅ Setup complete! Choose an option:"
echo ""
echo "1. Check Shakira tickets"
echo "2. Check Rockets tickets" 
echo "3. Enter custom event URL"
echo ""
read -p "Your choice (1-3): " choice

case $choice in
    1)
        echo "🎤 Checking Shakira tickets..."
        python check_any_event.py "https://www.axs.com/events/738037/shakira-tickets"
        ;;
    2)
        echo "🏀 Checking Rockets tickets..."
        python check_any_event.py "https://tix.axs.com/AQAAAAAAAADdMPEOBQAAAAA9%2Fv%2F%2F%2FwD%2F%2F%2F%2F%2FB3JvY2tldHMA%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8=/shop/search"
        ;;
    3)
        read -p "Enter event URL: " url
        python check_any_event.py "$url"
        ;;
    *)
        echo "Invalid choice"
        ;;
esac