# 📈 Market Tracker — Personal Finance Dashboard

A Python desktop application for tracking live stock, commodity, and ETF prices — with AI-powered portfolio analysis and a daily market briefing powered by Claude.

---

## ✨ Features

- **Live market prices** via `yfinance` (stocks, ETFs, commodities)
- **News feed** scraped from Reuters, BBC Business, and MarketWatch via RSS
- **AI Daily Briefing** — Claude analyses your portfolio and current market conditions
- **AI Chat Interface** — ask questions about your holdings and the market
- **Price Alerts** — get notified when assets hit your target prices
- **Portfolio tracker** — track holdings, cost basis, and P&L
- **Persistent database** — SQLite via SQLAlchemy ORM (PostgreSQL-ready)

---

## 🖥️ Tech Stack

| Layer | Technology |
|---|---|
| GUI | `customtkinter` |
| Market data | `yfinance` |
| News | `feedparser` (RSS) |
| Database | `SQLAlchemy` + `SQLite` |
| AI | Anthropic Claude API |
| Config | `python-dotenv` |

---

## ⚙️ Prerequisites

Before you start, make sure you have the following installed:

- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
- **Git** — [git-scm.com](https://git-scm.com/)
- **VS Code** (recommended) — [code.visualstudio.com](https://code.visualstudio.com/)

---

## 🚀 Setup Instructions

### 1. Clone the repository

```bash
git clone git@github.com:<your-username>/<your-repo>.git
cd <your-repo>
```

> **SSH not set up yet?** Ask the repo owner to share the HTTPS link, or set up an SSH key following [GitHub's guide](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

---

### 2. Create a virtual environment

A virtual environment keeps your project dependencies isolated from the rest of your system.

```bash
python -m venv venv
```

Then activate it:

```bash
# macOS / Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` appear at the start of your terminal prompt.

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Set up your `.env` file

Create a file called `.env` in the root of the project:

```bash
# macOS / Linux
touch .env

# Windows (Command Prompt)
type nul > .env
```

Open `.env` in your editor and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

> **Getting an API key:**
> 1. Go to [console.anthropic.com](https://console.anthropic.com)
> 2. Sign in or create an account
> 3. Navigate to **API Keys** and create a new key
> 4. Copy it directly into `.env` — **never paste it into chat, code, or anywhere else**

> ⚠️ The `.env` file is listed in `.gitignore` and will **never** be committed to GitHub. Keep your key safe.

---

### 5. Run the app

```bash
python main.py
```

The desktop window should open with all five tabs: **Markets, Portfolio, News, AI Analyst, Alerts**.

---

## 🗂️ Project Structure

```
├── main.py                  # App entry point
├── requirements.txt         # Python dependencies
├── .env                     # API keys (never commit this!)
├── .gitignore
│
├── models/                  # SQLAlchemy ORM models
│   └── ...
│
├── services/                # Business logic (data fetching, AI, alerts)
│   ├── fetcher_service.py   # yfinance price fetching
│   ├── news_service.py      # RSS news scraping
│   ├── ai_service.py        # Claude API calls
│   └── ...
│
├── repositories/            # Database access layer
│   └── ...
│
├── gui/                     # All GUI code
│   ├── tabs/                # One file per tab
│   │   ├── markets_tab.py
│   │   ├── portfolio_tab.py
│   │   ├── news_tab.py
│   │   ├── ai_tab.py
│   │   └── alerts_tab.py
│   └── components/          # Reusable UI components
│       ├── price_row.py
│       ├── news_card.py
│       ├── chat_bubble.py
│       └── ...
│
└── database/
    └── db.py                # SQLAlchemy engine & session setup
```

---

## 🏛️ Architecture

The app follows **MVC architecture** with a service layer:

- **Models** — define database tables via SQLAlchemy ORM
- **Repositories** — handle all database reads/writes (one session per operation)
- **Services** — contain all business logic; GUI never touches the DB directly
- **GUI/Tabs** — thin views that call services and display results
- **Components** — reusable widgets (PriceRow, NewsCard, ChatBubble, etc.)

---

## 🛠️ Common Issues

### `ModuleNotFoundError`
Make sure your virtual environment is activated — you should see `(venv)` in your terminal. Then run `pip install -r requirements.txt` again.

### `ANTHROPIC_API_KEY not found`
Make sure your `.env` file exists in the project root and contains the line:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### SQLite threading errors
All database sessions must be scoped per-operation, not shared across threads. Each service method should open and close its own session. The engine is configured with `check_same_thread=False`.

### App window doesn't open on Windows
Try running with `python main.py` from inside the activated virtual environment. If `customtkinter` throws a DPI error, add this near the top of `main.py`:
```python
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(1)
```

---

## 🔐 Security Rules

1. **Never paste your API key into chat, code files, or commit history**
2. **Always store keys in `.env` only**
3. `.env` is in `.gitignore` — confirm before your first `git push`
4. If you accidentally expose a key, rotate it immediately at [console.anthropic.com](https://console.anthropic.com)

---

## 📬 Questions?

Reach out to Stefano or open an issue in the repo.
