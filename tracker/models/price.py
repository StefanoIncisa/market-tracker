from sqlalchemy import Column, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base


class PriceSnapshot(Base):
    """
    A single price reading for an asset at a point in time.
    Every time we fetch prices, a snapshot is saved.
    This builds up historical price data over time.
    """
    __tablename__ = "price_snapshots"

    asset_id = Column(ForeignKey("assets.id"), nullable=False)
    price = Column(Float, nullable=False)
    change_pct = Column(Float, nullable=False)        # % change from previous close
    volume = Column(Float, nullable=True)             # trading volume if available
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    asset = relationship("Asset", backref="price_snapshots")

    @property
    def is_positive(self):
        """Returns True if price is up from previous close."""
        return self.change_pct >= 0

    def __repr__(self):
        direction = "▲" if self.is_positive else "▼"
        return f"<PriceSnapshot {self.asset.symbol} | ${self.price} | {direction}{abs(self.change_pct):.2f}%>"