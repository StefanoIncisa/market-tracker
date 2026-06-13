from sqlalchemy import Column, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base


class Holding(Base):
    """
    Represents an asset you currently own.
    Tracks quantity and average buy price.
    """
    __tablename__ = "holdings"

    asset_id = Column(ForeignKey("assets.id"), nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)
    average_buy_price = Column(Float, nullable=False, default=0.0)
    currency = Column(String, default="USD")

    # Relationships
    asset = relationship("Asset", backref="holdings")
    transactions = relationship("Transaction", back_populates="holding")

    @property
    def total_invested(self):
        return self.quantity * self.average_buy_price

    def __repr__(self):
        return f"<Holding {self.asset.symbol} | qty: {self.quantity} | avg: {self.average_buy_price}>"


class Transaction(Base):
    """
    Records every buy or sell action.
    Used to calculate average buy price and transaction history.
    """
    __tablename__ = "transactions"

    holding_id = Column(ForeignKey("holdings.id"), nullable=False)
    type = Column(String, nullable=False)        # "buy" | "sell"
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    holding = relationship("Holding", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction {self.type} {self.quantity} @ {self.price}>"