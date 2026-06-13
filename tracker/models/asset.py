from sqlalchemy import Column, String
from .base import Base


class Asset(Base):
    """
    Represents a trackable financial instrument.
    Examples: Apple (AAPL), Gold (GC=F), Bitcoin (BTC-USD)
    """
    __tablename__ = "assets"

    symbol = Column(String, unique=True, nullable=False)   # "AAPL"
    name = Column(String, nullable=False)                  # "Apple"
    category = Column(String, nullable=False)              # "stock" | "etf" | "commodity" | "crypto"
    currency = Column(String, default="USD")               # "USD" | "GBP"

    def __repr__(self):
        return f"<Asset {self.symbol} | {self.name} | {self.category}>"