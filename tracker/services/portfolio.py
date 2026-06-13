from tracker.services.base_service import BaseService
from tracker.repositories import HoldingRepository, AssetRepository
from tracker.models.portfolio import Holding


class PortfolioService(BaseService):
    """
    Handles all portfolio business logic.
    Each operation gets its own database session.
    """

    def __init__(self):
        super().__init__()

    def get_holdings(self) -> list[Holding]:
        """Returns all active holdings with asset data preloaded."""
        session = self._get_session()
        try:
            repo = HoldingRepository(session)
            return repo.get_active_holdings()
        except Exception as e:
            self._handle_error(e, "Failed to get holdings")
            return []
        finally:
            session.close()

    def get_summary(self, price_data: dict) -> dict:
        """Calculates overall portfolio summary stats."""
        session = self._get_session()
        try:
            repo = HoldingRepository(session)
            holdings = repo.get_active_holdings()

            total_invested = 0
            total_current = 0
            total_today_change = 0

            for holding in holdings:
                symbol = holding.asset.symbol
                snapshot = price_data.get(symbol)
                if not snapshot:
                    continue

                invested = holding.quantity * holding.average_buy_price
                current_val = holding.quantity * snapshot.price
                prev_price = snapshot.price / (1 + snapshot.change_pct / 100)
                today_change = holding.quantity * (snapshot.price - prev_price)

                total_invested += invested
                total_current += current_val
                total_today_change += today_change

            total_pnl = total_current - total_invested
            total_pnl_pct = (total_pnl / total_invested * 100) if total_invested else 0

            return {
                "total_invested":  total_invested,
                "total_current":   total_current,
                "total_pnl":       total_pnl,
                "total_pnl_pct":   total_pnl_pct,
                "total_today":     total_today_change,
            }
        except Exception as e:
            self._handle_error(e, "Failed to get portfolio summary")
            return {
                "total_invested": 0,
                "total_current":  0,
                "total_pnl":      0,
                "total_pnl_pct":  0,
                "total_today":    0,
            }
        finally:
            session.close()

    def get_position_data(self, holding: Holding, price_data: dict) -> dict | None:
        """Calculates P&L for a single holding."""
        try:
            symbol = holding.asset.symbol
            snapshot = price_data.get(symbol)

            if not snapshot:
                return None

            invested = holding.quantity * holding.average_buy_price
            current_val = holding.quantity * snapshot.price
            pnl = current_val - invested
            pnl_pct = (pnl / invested * 100) if invested else 0
            prev_price = snapshot.price / (1 + snapshot.change_pct / 100)
            today_change = holding.quantity * (snapshot.price - prev_price)

            return {
                "holding":      holding,
                "snapshot":     snapshot,
                "invested":     invested,
                "current_val":  current_val,
                "pnl":          pnl,
                "pnl_pct":      pnl_pct,
                "today_change": today_change,
            }
        except Exception as e:
            self._handle_error(e, f"Failed to get position data for {holding.asset.symbol}")
            return None

    def add_position(self, symbol: str, quantity: float, buy_price: float) -> Holding | None:
        """Adds a new position or increases an existing one."""
        session = self._get_session()
        try:
            asset_repo = AssetRepository(session)
            holding_repo = HoldingRepository(session)

            asset = asset_repo.get_by_symbol(symbol)
            if not asset:
                self._logger.warning(f"Asset not found: {symbol}")
                return None

            existing = holding_repo.get_by_asset(asset.id)

            if existing:
                return holding_repo.update_average_price(existing, quantity, buy_price)
            else:
                holding = Holding(
                    asset_id=asset.id,
                    quantity=quantity,
                    average_buy_price=buy_price,
                    currency=asset.currency
                )
                return holding_repo.save(holding)

        except Exception as e:
            self._handle_error(e, f"Failed to add position for {symbol}")
            return None
        finally:
            session.close()

    def remove_position(self, symbol: str, quantity: float) -> Holding | None:
        """Reduces a position by the given quantity."""
        session = self._get_session()
        try:
            asset_repo = AssetRepository(session)
            holding_repo = HoldingRepository(session)

            asset = asset_repo.get_by_symbol(symbol)
            if not asset:
                return None

            holding = holding_repo.get_by_asset(asset.id)
            if not holding:
                return None

            holding.quantity = max(0, holding.quantity - quantity)
            return holding_repo.update(holding)

        except Exception as e:
            self._handle_error(e, f"Failed to remove position for {symbol}")
            return None
        finally:
            session.close()