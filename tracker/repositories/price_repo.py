from datetime import datetime, timezone
from sqlalchemy.orm import Session
from tracker.models.price import PriceSnapshot
from .base_repo import BaseRepository


class PriceRepository(BaseRepository[PriceSnapshot]):
    """
    Handles all database operations for price snapshots.
    Builds up historical price data over time.
    """

    def __init__(self, session: Session):
        super().__init__(session, PriceSnapshot)

    def get_latest(self, asset_id: int) -> PriceSnapshot | None:
        """Fetch the most recent price snapshot for an asset."""
        return self._query().filter(
            PriceSnapshot.asset_id == asset_id
        ).order_by(PriceSnapshot.timestamp.desc()).first()

    def get_history(self, asset_id: int, limit: int = 100) -> list[PriceSnapshot]:
        """Fetch price history for an asset, most recent first."""
        return self._query().filter(
            PriceSnapshot.asset_id == asset_id
        ).order_by(PriceSnapshot.timestamp.desc()).limit(limit).all()

    def get_since(self, asset_id: int, since: datetime) -> list[PriceSnapshot]:
        """Fetch all price snapshots for an asset since a given datetime."""
        return self._query().filter(
            PriceSnapshot.asset_id == asset_id,
            PriceSnapshot.timestamp >= since
        ).order_by(PriceSnapshot.timestamp.asc()).all()

    def get_latest_all(self) -> list[PriceSnapshot]:
        """
        Fetch the most recent snapshot for every asset.
        Used to populate the markets view on startup.
        """
        subquery = self._query().with_entities(
            PriceSnapshot.asset_id,
        ).distinct(PriceSnapshot.asset_id).subquery()

        return self._query().filter(
            PriceSnapshot.asset_id.in_(subquery)
        ).order_by(
            PriceSnapshot.asset_id,
            PriceSnapshot.timestamp.desc()
        ).all()