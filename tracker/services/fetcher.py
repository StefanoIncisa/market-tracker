import threading
import yfinance as yf
from datetime import datetime, timezone
from tracker.services.base_service import BaseService
from tracker.repositories import AssetRepository, PriceRepository
from tracker.models.price import PriceSnapshot


class PriceFetcherService(BaseService):
    """
    Fetches live prices for all tracked assets using yfinance.
    Runs in a background thread so it never blocks the GUI.
    Saves every price fetch as a PriceSnapshot to the database.
    """

    def __init__(self, on_update=None):
        super().__init__()
        self.__thread = None
        self.__running = False
        self.__on_update = on_update  # callback function to notify GUI of new prices

        self.__asset_repo = AssetRepository(self._session)
        self.__price_repo = PriceRepository(self._session)

    def fetch_all(self) -> dict:
        """
        Fetches live prices for all assets in the database.
        Returns a dict of {symbol: PriceSnapshot}.
        Also saves each snapshot to the database.
        """
        assets = self.__asset_repo.get_all()
        results = {}

        for asset in assets:
            snapshot = self._fetch_one(asset)
            if snapshot:
                results[asset.symbol] = snapshot

        # Notify the GUI that new prices are available
        if self.__on_update:
            self.__on_update(results)

        return results

    def _fetch_one(self, asset) -> PriceSnapshot | None:
        """
        Protected — fetches and saves a single asset's price.
        Only called internally by fetch_all.
        """
        try:
            ticker = yf.Ticker(asset.symbol)
            info = ticker.fast_info

            current = info.last_price
            prev_close = info.previous_close

            if not current or not prev_close:
                return None

            change_pct = ((current - prev_close) / prev_close) * 100

            snapshot = PriceSnapshot(
                asset_id=asset.id,
                price=current,
                change_pct=change_pct,
                volume=getattr(info, "three_month_average_volume", None),
                timestamp=datetime.now(timezone.utc)
            )

            return self.__price_repo.save(snapshot)

        except Exception as e:
            self._handle_error(e, f"Failed to fetch price for {asset.symbol}")
            return None

    def start_background_loop(self, interval_seconds: int = 60):
        """
        Starts fetching prices in a background thread every interval_seconds.
        The GUI stays responsive while this runs in the background.
        """
        self.__running = True
        self.__thread = threading.Thread(
            target=self.__loop,
            args=(interval_seconds,),
            daemon=True  # thread dies automatically when app closes
        )
        self.__thread.start()
        self._logger.info("Price fetcher started")

    def stop(self):
        """Stops the background fetching loop."""
        self.__running = False
        self._logger.info("Price fetcher stopped")

    def __loop(self, interval_seconds: int):
        """
        Private — the actual background loop.
        Nobody outside this class should call this directly.
        """
        import time
        while self.__running:
            try:
                self.fetch_all()
            except Exception as e:
                self._handle_error(e, "Error in price fetch loop")
            time.sleep(interval_seconds)