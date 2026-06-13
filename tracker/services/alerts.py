import threading
from datetime import datetime, timezone
from tracker.services.base_service import BaseService
from tracker.repositories import AlertRepository, AlertLogRepository, AssetRepository
from tracker.models.alert import Alert, AlertLog


class AlertService(BaseService):
    """
    Monitors active alerts and triggers them when conditions are met.
    Each operation gets its own database session.
    """

    def __init__(self, on_alert=None):
        super().__init__()
        self.__on_alert = on_alert

    def check_all(self, price_data: dict) -> list[AlertLog]:
        """Checks all active alerts against current price data."""
        session = self._get_session()
        try:
            alert_repo = AlertRepository(session)
            alert_log_repo = AlertLogRepository(session)
            asset_repo = AssetRepository(session)
            triggered = []

            for alert in alert_repo.get_active():
                asset = asset_repo.get_by_id(alert.asset_id)
                if not asset:
                    continue

                snapshot = price_data.get(asset.symbol)
                if not snapshot:
                    continue

                if alert._is_triggered(snapshot.price, snapshot.change_pct):
                    log = self._trigger(alert, snapshot, alert_log_repo)
                    if log:
                        triggered.append(log)

            return triggered
        except Exception as e:
            self._handle_error(e, "Failed to check alerts")
            return []
        finally:
            session.close()

    def _trigger(self, alert: Alert, snapshot, alert_log_repo) -> AlertLog | None:
        """Protected — fires an alert and saves it to the log."""
        try:
            log = AlertLog(
                alert_id=alert.id,
                triggered_at=datetime.now(timezone.utc),
                price_at_trigger=snapshot.price,
                change_pct_at_trigger=snapshot.change_pct
            )
            saved_log = alert_log_repo.save(log)

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
        """Creates a new alert for an asset."""
        session = self._get_session()
        try:
            asset_repo = AssetRepository(session)
            alert_repo = AlertRepository(session)

            asset = asset_repo.get_by_symbol(symbol)
            if not asset:
                self._logger.warning(f"Asset not found: {symbol}")
                return None

            alert = Alert(
                asset_id=asset.id,
                condition=condition,
                threshold=threshold,
                active=True
            )
            return alert_repo.save(alert)

        except Exception as e:
            self._handle_error(e, f"Failed to create alert for {symbol}")
            return None
        finally:
            session.close()

    def deactivate_alert(self, alert_id: int) -> bool:
        """Deactivates an alert by ID."""
        session = self._get_session()
        try:
            alert_repo = AlertRepository(session)
            alert = alert_repo.get_by_id(alert_id)
            if alert:
                alert_repo.deactivate(alert)
                return True
            return False
        except Exception as e:
            self._handle_error(e, f"Failed to deactivate alert {alert_id}")
            return False
        finally:
            session.close()