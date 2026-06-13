from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from tracker.models.base import Base
from tracker.models import Asset, Holding, Transaction, PriceSnapshot, NewsArticle, Alert, AlertLog
import config
import os


class Database:
    """
    Singleton database connection manager.
    Only one instance of this class exists in the app.
    All repositories share the same connection.
    """

    _instance = None

    def __new__(cls):
        """Ensures only one Database instance is ever created."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self):
        if self._initialised:
            return

        # Create the data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        # Create the database engine
        self.__engine = create_engine(
            f"sqlite:///{config.DATABASE_PATH}",
            echo=False,
            connect_args={"check_same_thread": False}
        )
        
        # Create a session factory
        self.__SessionFactory = sessionmaker(bind=self.__engine)

        # Create all tables if they don't exist yet
        Base.metadata.create_all(self.__engine)

        self._initialised = True
        print("✅ Database initialised successfully")

    def get_session(self) -> Session:
        """Returns a new database session."""
        return self.__SessionFactory()

    def create_tables(self):
        """Creates all tables — safe to call multiple times."""
        Base.metadata.create_all(self.__engine)

    @staticmethod
    def seed_assets():
        """
        Populates the assets table with default tracked assets on first run.
        Safe to call multiple times — skips assets that already exist.
        """
        db = Database()
        session = db.get_session()

        from tracker.repositories import AssetRepository
        repo = AssetRepository(session)

        default_assets = [
            {"symbol": "CL=F",    "name": "Oil (WTI)",  "category": "commodity", "currency": "USD"},
            {"symbol": "GC=F",    "name": "Gold",        "category": "commodity", "currency": "USD"},
            {"symbol": "VWRL.L",  "name": "VWRL",        "category": "etf",       "currency": "GBP"},
            {"symbol": "VUSA.L",  "name": "VUSA",        "category": "etf",       "currency": "GBP"},
            {"symbol": "SPY",     "name": "S&P 500",     "category": "etf",       "currency": "USD"},
            {"symbol": "AAPL",    "name": "Apple",       "category": "stock",     "currency": "USD"},
            {"symbol": "TSLA",    "name": "Tesla",       "category": "stock",     "currency": "USD"},
            {"symbol": "MSFT",    "name": "Microsoft",   "category": "stock",     "currency": "USD"},
            {"symbol": "AMZN",    "name": "Amazon",      "category": "stock",     "currency": "USD"},
            {"symbol": "BTC-USD", "name": "Bitcoin",     "category": "crypto",    "currency": "USD"},
            {"symbol": "ETH-USD", "name": "Ethereum",    "category": "crypto",    "currency": "USD"},
        ]

        for asset_data in default_assets:
            if not repo.get_by_symbol(asset_data["symbol"]):
                asset = Asset(**asset_data)
                repo.save(asset)

        session.close()
        print("✅ Assets seeded successfully")