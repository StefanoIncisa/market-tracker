from sqlalchemy.orm import Session
from tracker.models.alert import Alert, AlertLog
from tracker.models.asset import Asset
from .base_repo import BaseRepository


class AlertRepository(BaseRepository[Alert]):
    """
    Handles all database operations for alerts.
    """

    def __init__(self, session: Session):
        super().__init__(session, Alert)

    def get_active(self) -> list[Alert]:
        """Fetch all alerts that are currently active."""
        return self._query().filter(
            Alert.active == True
        ).all()

    def get_by_asset(self, asset_id: int) -> list[Alert]:
        """Fetch all alerts for a specific asset."""
        return self._query().filter(
            Alert.asset_id == asset_id
        ).all()

    def get_active_by_asset(self, asset_id: int) -> list[Alert]:
        """Fetch only active alerts for a specific asset."""
        return self._query().filter(
            Alert.asset_id == asset_id,
            Alert.active == True
        ).all()

    def deactivate(self, alert: Alert) -> Alert:
        """Turn off an alert without deleting it."""
        alert.active = False
        return self.update(alert)

    def activate(self, alert: Alert) -> Alert:
        """Turn an alert back on."""
        alert.active = True
        return self.update(alert)


class AlertLogRepository(BaseRepository[AlertLog]):
    """
    Handles all database operations for alert history.
    """

    def __init__(self, session: Session):
        super().__init__(session, AlertLog)

    def get_by_alert(self, alert_id: int) -> list[AlertLog]:
        """Fetch all times a specific alert has fired."""
        return self._query().filter(
            AlertLog.alert_id == alert_id
        ).order_by(AlertLog.triggered_at.desc()).all()

    def get_recent(self, limit: int = 20) -> list[AlertLog]:
        """Fetch the most recently triggered alerts across all assets."""
        return self._query().order_by(
            AlertLog.triggered_at.desc()
        ).limit(limit).all()