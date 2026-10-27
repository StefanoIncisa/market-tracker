# 📈 Market Tracker

A Python desktop app for following the markets in one place. It tracks live prices for stocks, ETFs, commodities and crypto, keeps a portfolio with P&L, pulls in financial news, fires price alerts and includes an AI analyst powered by the Anthropic Claude API.

I built it to combine my finance background with what I have been learning as a developer: a layered architecture, an ORM-backed database and a real LLM integration.

## Features

- **Live markets** for stocks, ETFs, commodities and crypto via `yfinance`
- **Portfolio tracker** with holdings, cost basis and profit and loss
- **Price alerts** when an asset moves past a set threshold
- **News feed** from Reuters, BBC Business and MarketWatch RSS
- **AI Analyst** tab: a daily briefing on your portfolio and a chat to ask questions about your holdings and the market, powered by Claude
- **Persistent storage** with SQLAlchemy and SQLite (PostgreSQL-ready)

## Tech stack

| Layer | Technology |
| --- | --- |
| GUI | customtkinter |
| Market data | yfinance |
| News | feedparser (RSS) |
| Database | SQLAlchemy ORM + SQLite |
| AI | Anthropic Claude API |
| Config | python-dotenv |

## Architecture

The app is split into layers so each part has one job:

```
GUI (tabs + reusable components)
        │
Controller (app_controller.py)
        │
Services (prices, news, alerts, portfolio, AI analyst)
        │
Repositories (all database reads and writes)
        │
Models (SQLAlchemy tables)
```

- **Models** define the database tables
- **Repositories** handle every read and write, with one session per operation
- **Services** hold the business logic, so the GUI never touches the database directly
- **GUI** tabs are thin views, built from reusable widgets like `PriceRow`, `NewsCard` and `ChatBubble`

## Project structure

```
market-tracker/
├── main.py                 # Entry point
├── config.py               # Tracked assets, RSS feeds, refresh settings
├── requirements.txt
└── tracker/
    ├── database.py         # Engine and session setup
    ├── models/             # asset, price, portfolio, alert, news
    ├── repositories/       # one repository per model
    ├── services/           # fetcher, news, alerts, portfolio, ai_analyst
    ├── controllers/        # app_controller.py
    └── gui/
        ├── app.py
        ├── markets_tab.py, portfolio_tab.py, news_tab.py,
        │   analyst_tab.py, alerts_tab.py
        └── components/     # price_row, news_card, chat_bubble, stat_card, ...
```

## Getting started

Requires Python 3.10+.

```bash
git clone https://github.com/StefanoIncisa/market-tracker.git
cd market-tracker

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file in the project root with your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

Then run:

```bash
python main.py
```

The window opens with five tabs: Markets, Portfolio, News, AI Analyst and Alerts.

> The `.env` file is listed in `.gitignore`, so the key is never committed.

## Troubleshooting

- **`ModuleNotFoundError`**: activate the virtual environment and run `pip install -r requirements.txt` again.
- **`ANTHROPIC_API_KEY not found`**: check that `.env` exists in the project root and contains the key.
- **SQLite threading errors**: each service method opens and closes its own session, and the engine uses `check_same_thread=False`.
