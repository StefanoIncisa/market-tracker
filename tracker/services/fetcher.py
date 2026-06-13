import threading
import yfinance as yf
from datetime import datetime, timezone
from tracker.services.base_service import BaseService
from tracker.repositories import AssetRepository, PriceRepository
from tracker.models.price import PriceSnapshot


class PriceData:
    """
    Plain data object — holds price info without any database connection.
    Safe to pass to the GUI after the session closes.
    """
    def __init__(self, symbol: str, name: str, category: str, currency: str,
                 price: float, change_pct: float, volume: float):
        self.symbol = symbol
        self.name = name
        self.category = category
        self.currency = currency
        self.price = price
        self.change_pct = change_pct
        self.volume = volume

    @property
    def is_positive(self):
        return self.change_pct >= 0


class PriceFetcherService(BaseService):
    """
    Fetches live prices for all tracked assets using yfinance.
    Returns plain PriceData objects safe to use after session closes.
    """

    def __init__(self, on_update=None):
        super().__init__()
        self.__running = False
        self.__thread = None
        self.__on_update = on_update

    def fetch_all(self) -> dict:
        """Fetches live prices for all assets. Returns {symbol: PriceData}."""
        session = self._get_session()
        try:
            asset_repo = AssetRepository(session)
            assets = asset_repo.get_all()
            results = {}

            for asset in assets:
                price_data = self._fetch_one(asset, session)
                if price_data:
                    results[asset.symbol] = price_data

            if self.__on_update:
                self.__on_update(results)

            return results
        except Exception as e:
            self._handle_error(e, "Failed to fetch all prices")
            return {}
        finally:
            session.close()

    def _fetch_one(self, asset, session) -> PriceData | None:
        """Protected — fetches price and returns a plain PriceData object."""
        try:
            ticker = yf.Ticker(asset.symbol)
            info = ticker.fast_info

            current = info.last_price
            prev_close = info.previous_close

            if not current or not prev_close:
                return None

            change_pct = ((current - prev_close) / prev_close) * 100
            volume = getattr(info, "three_month_average_volume", None)

            # Save snapshot to database
            snapshot = PriceSnapshot(
                asset_id=asset.id,
                price=current,
                change_pct=change_pct,
                volume=volume,
                timestamp=datetime.now(timezone.utc)
            )
            price_repo = PriceRepository(session)
            price_repo.save(snapshot)

            # Return plain object — no database dependency
            return PriceData(
                symbol=asset.symbol,
                name=asset.name,
                category=asset.category,
                currency=asset.currency,
                price=current,
                change_pct=change_pct,
                volume=volume
            )

        except Exception as e:
            self._handle_error(e, f"Failed to fetch price for {asset.symbol}")
            return None

    def start_background_loop(self, interval_seconds: int = 60):
        """Starts fetching prices in a background thread."""
        self.__running = True
        self.__thread = threading.Thread(
            target=self.__loop,
            args=(interval_seconds,),
            daemon=True
        )
        self.__thread.start()
        self._logger.info("Price fetcher started")

    def stop(self):
        self.__running = False
        self._logger.info("Price fetcher stopped")

    def __loop(self, interval_seconds: int):
        import time
        while self.__running:
            try:
                self.fetch_all()
            except Exception as e:
                self._handle_error(e, "Error in price fetch loop")
            time.sleep(interval_seconds)