from typing import Optional
from sqlalchemy.orm import Session
from tracker.models.portfolio import Holding, Transaction
from tracker.models.asset import Asset
from .base_repo import BaseRepository


class HoldingRepository(BaseRepository[Holding]):
    """
    Handles all database operations for holdings.
    Inherits standard CRUD from BaseRepository.
    Adds portfolio-specific queries on top.
    """

    def __init__(self, session: Session):
        super().__init__(session, Holding)

    def get_by_asset(self, asset_id: int) -> Optional[Holding]:
        """Find a holding by asset ID."""
        return self._query().filter(Holding.asset_id == asset_id).first()

    def get_all_with_assets(self) -> list[Holding]:
        """Fetch all holdings with their asset data preloaded."""
        return self._query().join(Asset).all()

    def get_active_holdings(self) -> list[Holding]:
        """Only return holdings where quantity is greater than zero."""
        return self._query().filter(Holding.quantity > 0).all()

    def update_average_price(self, holding: Holding, new_qty: float, new_price: float) -> Holding:
        """
        Recalculates average buy price when adding to a position.
        Uses weighted average formula.
        """
        total_qty = holding.quantity + new_qty
        if total_qty == 0:
            holding.average_buy_price = 0.0
        else:
            holding.average_buy_price = (
                (holding.quantity * holding.average_buy_price) + (new_qty * new_price)
            ) / total_qty
        holding.quantity = total_qty
        return self.update(holding)


class TransactionRepository(BaseRepository[Transaction]):
    """
    Handles all database operations for transactions.
    """

    def __init__(self, session: Session):
        super().__init__(session, Transaction)

    def get_by_holding(self, holding_id: int) -> list[Transaction]:
        """Fetch all transactions for a specific holding."""
        return self._query().filter(
            Transaction.holding_id == holding_id
        ).order_by(Transaction.date.desc()).all()

    def get_recent(self, limit: int = 10) -> list[Transaction]:
        """Fetch the most recent transactions across all holdings."""
        return self._query().order_by(
            Transaction.date.desc()
        ).limit(limit).all()