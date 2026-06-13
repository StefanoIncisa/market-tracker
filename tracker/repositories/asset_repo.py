from sqlalchemy.orm import Session
from tracker.models.asset import Asset
from .base_repo import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    """
    Handles all database operations for assets.
    """

    def __init__(self, session: Session):
        super().__init__(session, Asset)

    def get_by_symbol(self, symbol: str) -> Asset | None:
        """Fetch an asset by its ticker symbol."""
        return self._query().filter(Asset.symbol == symbol).first()

    def get_by_category(self, category: str) -> list[Asset]:
        """Fetch all assets in a category — stock, etf, commodity, crypto."""
        return self._query().filter(Asset.category == category).all()

    def get_all_symbols(self) -> list[str]:
        """Returns just the ticker symbols of all tracked assets."""
        return [asset.symbol for asset in self.get_all()]