# Toyota Center Ticket Tracker 🎫

Real-time ticket price tracking and monitoring for Toyota Center events in Houston. Get notified when ticket prices drop!

![Dashboard Preview](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Features

- **Real-time Price Monitoring** - Track ticket prices across all sections
- **Price Drop Alerts** - Get notified when prices decrease
- **Beautiful Dashboard** - Visual charts and live updates
- **Multi-Event Support** - Monitor multiple events simultaneously
- **Historical Data** - Track price trends over time
- **AXS Integration** - Works with official AXS ticketing platform

## 🚀 Quick Start

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/toyota-center-tracker.git
cd toyota-center-tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the dashboard:
```bash
python start_dashboard.py
```

4. Open http://localhost:8080 in your browser

### Check Specific Events

```bash
# Check Shakira tickets
python check_any_event.py

# Check with custom URL
python check_any_event.py "https://your-event-url"
```

## 🚄 Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/deploy?referralCode=)

1. Click the button above
2. Connect your GitHub account
3. Deploy!

### Manual Railway Setup

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Deploy:
```bash
railway up
```

4. Add environment variables in Railway dashboard:
```
DATABASE_URL=your_database_url
```

## 📊 Dashboard Features

- **Live Price Updates** - Real-time ticket availability and pricing
- **Price History Charts** - Visualize price trends by section
- **Drop Notifications** - See all recent price decreases
- **Event Management** - Add and monitor multiple events

## 🛠️ API Endpoints

- `GET /` - Dashboard interface
- `GET /events` - List all events
- `GET /events/{name}/tickets` - Get ticket prices for an event
- `POST /axs/check` - Check prices from AXS URL
- `GET /price-drops` - Recent price drops
- `GET /events/{name}/history` - Price history for an event

## 📁 Project Structure

```
toyota-center-tracker/
├── api/               # FastAPI backend
│   └── main.py       # API routes and logic
├── scrapers/         # Web scraping modules
│   ├── toyota_center_scraper.py
│   └── axs_scraper.py
├── models/           # Database models
│   └── database.py
├── dashboard/        # Web interface
│   ├── index.html
│   └── dashboard.js
├── utils/            # Utility functions
└── requirements.txt  # Python dependencies
```

## 🔧 Configuration

Create a `.env` file:
```env
DATABASE_URL=sqlite:///./toyota_center_tickets.db
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with FastAPI and Selenium
- Uses undetected-chromedriver for reliable scraping
- Chart.js for beautiful visualizations

---

Made with ❤️ for Houston event-goers