import logging
from tracker.database import Database
from sqlalchemy.orm import Session


class BaseService:
    """
    Parent class for all services.
    Provides shared access to the database, logging,
    and error handling that every service inherits.
    """

    def __init__(self):
        self._db = Database()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._session: Session = self._db.get_session()

    def _handle_error(self, error: Exception, message: str = "") -> None:
        """
        Protected method — logs errors consistently across all services.
        Services call this internally when something goes wrong.
        """
        self._logger.error(f"{message}: {str(error)}")

    def _close_session(self) -> None:
        """
        Protected method — closes the database session cleanly.
        Called when a service is done with its work.
        """
        if self._session:
            self._session.close()

    def __del__(self):
        """Automatically closes the session when the service is destroyed."""
        self._close_session()