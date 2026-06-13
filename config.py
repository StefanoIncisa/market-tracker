import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─── API KEYS ────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# ─── ASSETS TO TRACK ─────────────────────────────────────────────────────────
ASSETS = {
    # Commodities
    "Oil (WTI)":  "CL=F",
    "Gold":       "GC=F",

    # ETFs
    "VWRL":       "VWRL.L",
    "VUSA":       "VUSA.L",
    "S&P 500":    "SPY",

    # Stocks
    "Apple":      "AAPL",
    "Tesla":      "TSLA",
    "Microsoft":  "MSFT",
    "Amazon":     "AMZN",

    # Crypto
    "Bitcoin":    "BTC-USD",
    "Ethereum":   "ETH-USD",
}

# ─── NEWS RSS FEEDS ──────────────────────────────────────────────────────────
NEWS_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://feeds.marketwatch.com/marketwatch/topstories",
]

# ─── SETTINGS ─────────────────────────────────────────────────────────────────
ALERT_THRESHOLD = 2.0
REFRESH_SECONDS = 60
NEWS_REFRESH_MINUTES = 15

# ─── DATABASE ─────────────────────────────────────────────────────────────────
DATABASE_PATH = "data/portfolio.db"