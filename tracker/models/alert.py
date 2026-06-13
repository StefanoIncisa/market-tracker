from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base


class Alert(Base):
    """
    A price alert set by the user for a specific asset.
    Example: notify me when Apple goes above $300
    """
    __tablename__ = "alerts"

    asset_id = Column(ForeignKey("assets.id"), nullable=False)
    condition = Column(String, nullable=False)    # "above" | "below" | "change_pct"
    threshold = Column(Float, nullable=False)     # the price or % to trigger at
    active = Column(Boolean, default=True)        # can be toggled on/off

    # Relationships
    asset = relationship("Asset", backref="alerts")
    logs = relationship("AlertLog", back_populates="alert")

    def _is_triggered(self, current_price, change_pct):
        """
        Internal method — checks if current market data triggers this alert.
        Only AlertService should call this.
        """
        if self.condition == "above":
            return current_price >= self.threshold
        elif self.condition == "below":
            return current_price <= self.threshold
        elif self.condition == "change_pct":
            return abs(change_pct) >= self.threshold
        return False

    def __repr__(self):
        return f"<Alert {self.asset.symbol} | {self.condition} {self.threshold} | active: {self.active}>"


class AlertLog(Base):
    """
    Records every time an alert is triggered.
    Gives you a history of when your alerts fired and at what price.
    """
    __tablename__ = "alert_logs"

    alert_id = Column(ForeignKey("alerts.id"), nullable=False)
    triggered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    price_at_trigger = Column(Float, nullable=False)
    change_pct_at_trigger = Column(Float, nullable=True)

    # Relationships
    alert = relationship("Alert", back_populates="logs")

    def __repr__(self):
        return f"<AlertLog alert:{self.alert_id} | ${self.price_at_trigger} @ {self.triggered_at}>"