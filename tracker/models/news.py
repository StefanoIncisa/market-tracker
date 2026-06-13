from sqlalchemy import Column, String, Text, DateTime, JSON
from datetime import datetime, timezone
from .base import Base


class NewsArticle(Base):
    """
    A financial news article fetched from RSS feeds.
    Stores the raw article plus AI-generated analysis.
    """
    __tablename__ = "news_articles"

    title = Column(String, nullable=False)
    source = Column(String, nullable=False)           # "Reuters" | "BBC" etc
    url = Column(String, unique=True, nullable=False) # prevents duplicate articles
    published_at = Column(DateTime, nullable=False)

    # AI generated fields — populated after Claude analyses the article
    summary = Column(Text, nullable=True)             # plain english summary
    affected_assets = Column(JSON, nullable=True)     # ["AAPL", "TSLA"] etc
    sentiment = Column(String, nullable=True)         # "positive" | "negative" | "neutral"
    impact_analysis = Column(Text, nullable=True)     # how it affects your portfolio

    @property
    def is_analysed(self):
        """Returns True if Claude has already analysed this article."""
        return self.summary is not None

    @property
    def sentiment_emoji(self):
        """Returns an emoji for the sentiment."""
        return {
            "positive": "🟢",
            "negative": "🔴",
            "neutral":  "🟡"
        }.get(self.sentiment, "⚪")

    def __repr__(self):
        return f"<NewsArticle {self.source} | {self.title[:50]}>"