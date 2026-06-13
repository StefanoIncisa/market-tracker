import threading
from datetime import datetime, timezone
from tracker.services.base_service import BaseService
from tracker.repositories import AlertRepository, AlertLogRepository, AssetRepository
from tracker.models.alert import Alert, AlertLog


class AlertService(BaseService):
    """
    Monitors active alerts and triggers them when conditions are met.
    Runs checks every time new price data comes in.
    """

    def __init__(self, on_alert=None):
        super().__init__()
        self.__alert_repo = AlertRepository(self._session)
        self.__alert_log_repo = AlertLogRepository(self._session)
        self.__asset_repo = AssetRepository(self._session)
        self.__on_alert = on_alert  # callback to notify GUI when alert fires

    def check_all(self, price_data: dict) -> list[AlertLog]:
        """
        Checks all active alerts against current price data.
        Called every time the price fetcher returns new data.
        price_data: {symbol: PriceSnapshot}
        """
        triggered = []
        active_alerts = self.__alert_repo.get_active()

        for alert in active_alerts:
            asset = self.__asset_repo.get_by_id(alert.asset_id)
            if not asset:
                continue

            snapshot = price_data.get(asset.symbol)
            if not snapshot:
                continue

            if alert._is_triggered(snapshot.price, snapshot.change_pct):
                log = self._trigger(alert, snapshot)
                if log:
                    triggered.append(log)

        return triggered

    def _trigger(self, alert: Alert, snapshot) -> AlertLog | None:
        """
        Protected — fires an alert and saves it to the log.
        Only called internally by check_all.
        """
        try:
            log = AlertLog(
                alert_id=alert.id,
                triggered_at=datetime.now(timezone.utc),
                price_at_trigger=snapshot.price,
                change_pct_at_trigger=snapshot.change_pct
            )
            saved_log = self.__alert_log_repo.save(log)

            # Notify the GUI
            if self.__on_alert:
                self.__on_alert(alert, saved_log)

            self._logger.info(
                f"Alert triggered: {alert.condition} {alert.threshold} "
                f"for asset {alert.asset_id} at ${snapshot.price}"
            )

            return saved_log

        except Exception as e:
            self._handle_error(e, f"Failed to trigger alert {alert.id}")
            return None

    def create_alert(self, symbol: str, condition: str, threshold: float) -> Alert | None:
        """
        Creates a new alert for an asset.
        condition: 'above' | 'below' | 'change_pct'
        threshold: the price or % value to trigger at
        """
        try:
            asset = self.__asset_repo.get_by_symbol(symbol)
            if not asset:
                self._logger.warning(f"Asset not found: {symbol}")
                return None

            alert = Alert(
                asset_id=asset.id,
                condition=condition,
                threshold=threshold,
                active=True
            )
            return self.__alert_repo.save(alert)

        except Exception as e:
            self._handle_error(e, f"Failed to create alert for {symbol}")
            return None

    def deactivate_alert(self, alert_id: int) -> bool:
        """Deactivates an alert by ID."""
        try:
            alert = self.__alert_repo.get_by_id(alert_id)
            if alert:
                self.__alert_repo.deactivate(alert)
                return True
            return False
        except Exception as e:
            self._handle_error(e, f"Failed to deactivate alert {alert_id}")
            return False