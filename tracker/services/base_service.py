import logging
from tracker.database import Database


class BaseService:
    """
    Parent class for all services.
    Each operation gets a fresh session to avoid threading conflicts.
    """

    def __init__(self):
        self._db = Database()
        self._logger = logging.getLogger(self.__class__.__name__)

    def _get_session(self):
        """Returns a fresh session for each operation."""
        return self._db.get_session()

    def _handle_error(self, error: Exception, message: str = "") -> None:
        self._logger.error(f"{message}: {str(error)}")