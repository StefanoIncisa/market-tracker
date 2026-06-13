from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, Optional
from tracker.models.base import Base

# Generic type so the repository works with any model
T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """
    Parent class for all repositories.
    Provides standard CRUD operations that every repository inherits.
    Create, Read, Update, Delete — the four basic database operations.
    """

    def __init__(self, session: Session, model: Type[T]):
        self.__session = session
        self._model = model

    def get_by_id(self, id: int) -> Optional[T]:
        """Fetch a single record by its ID."""
        return self.__session.get(self._model, id)

    def get_all(self) -> list[T]:
        """Fetch all records of this model."""
        return self.__session.query(self._model).all()

    def save(self, record: T) -> T:
        """Save a new record to the database."""
        self.__session.add(record)
        self.__session.commit()
        self.__session.refresh(record)
        return record

    def update(self, record: T) -> T:
        """Update an existing record."""
        self.__session.commit()
        self.__session.refresh(record)
        return record

    def delete(self, record: T) -> None:
        """Delete a record from the database."""
        self.__session.delete(record)
        self.__session.commit()

    def _query(self):
        """
        Protected method — gives subclasses access to build custom queries.
        Only repositories should use this, not services or GUI.
        """
        return self.__session.query(self._model)