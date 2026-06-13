from datetime import datetime
from sqlalchemy.orm import Session
from tracker.models.news import NewsArticle
from .base_repo import BaseRepository


class NewsRepository(BaseRepository[NewsArticle]):
    """
    Handles all database operations for news articles.
    Prevents duplicates and tracks which articles have been analysed by AI.
    """

    def __init__(self, session: Session):
        super().__init__(session, NewsArticle)

    def exists(self, url: str) -> bool:
        """Check if an article already exists by URL — prevents duplicates."""
        return self._query().filter(NewsArticle.url == url).count() > 0

    def get_unanalysed(self) -> list[NewsArticle]:
        """Fetch articles that Claude hasn't summarised yet."""
        return self._query().filter(
            NewsArticle.summary == None
        ).order_by(NewsArticle.published_at.desc()).all()

    def get_recent(self, limit: int = 20) -> list[NewsArticle]:
        """Fetch the most recent articles, analysed or not."""
        return self._query().order_by(
            NewsArticle.published_at.desc()
        ).limit(limit).all()

    def get_analysed(self, limit: int = 20) -> list[NewsArticle]:
        """Fetch only articles that have been analysed by Claude."""
        return self._query().filter(
            NewsArticle.summary != None
        ).order_by(NewsArticle.published_at.desc()).limit(limit).all()

    def get_by_sentiment(self, sentiment: str) -> list[NewsArticle]:
        """Fetch articles filtered by sentiment — positive, negative, neutral."""
        return self._query().filter(
            NewsArticle.sentiment == sentiment
        ).order_by(NewsArticle.published_at.desc()).all()

    def get_affecting_asset(self, symbol: str) -> list[NewsArticle]:
        """Fetch articles that affect a specific asset symbol."""
        return self._query().filter(
            NewsArticle.affected_assets.contains(symbol)
        ).order_by(NewsArticle.published_at.desc()).all()
        