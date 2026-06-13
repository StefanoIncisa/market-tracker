import threading
import feedparser
from datetime import datetime, timezone
from tracker.services.base_service import BaseService
from tracker.repositories import NewsRepository
from tracker.models.news import NewsArticle
import config


class NewsFetcherService(BaseService):
    """
    Fetches financial news from RSS feeds.
    Each fetch operation gets its own database session.
    """

    def __init__(self, on_update=None):
        super().__init__()
        self.__running = False
        self.__thread = None
        self.__on_update = on_update

    def fetch_all_feeds(self) -> list[NewsArticle]:
        """Fetches all configured RSS feeds and saves new articles."""
        session = self._get_session()
        try:
            news_repo = NewsRepository(session)
            new_articles = []

            for feed_url in config.NEWS_FEEDS:
                try:
                    articles = self._parse_feed(feed_url, news_repo)
                    new_articles.extend(articles)
                except Exception as e:
                    self._handle_error(e, f"Failed to fetch feed: {feed_url}")

            if self.__on_update and new_articles:
                self.__on_update(new_articles)

            return new_articles
        except Exception as e:
            self._handle_error(e, "Failed to fetch all feeds")
            return []
        finally:
            session.close()

    def _parse_feed(self, url: str, news_repo: NewsRepository) -> list[NewsArticle]:
        """Protected — parses a single RSS feed URL."""
        feed = feedparser.parse(url)
        source = feed.feed.get("title", "Unknown")
        new_articles = []

        for entry in feed.entries:
            article_url = entry.get("link", "")

            if news_repo.exists(article_url):
                continue

            published_at = self._parse_date(entry)

            article = NewsArticle(
                title=entry.get("title", "No title"),
                source=source,
                url=article_url,
                published_at=published_at,
            )

            saved = news_repo.save(article)
            new_articles.append(saved)

        return new_articles

    def _parse_date(self, entry) -> datetime:
        """Protected — extracts and parses the publication date."""
        try:
            time_struct = entry.get("published_parsed") or entry.get("updated_parsed")
            if time_struct:
                return datetime(*time_struct[:6], tzinfo=timezone.utc)
        except Exception:
            pass
        return datetime.now(timezone.utc)

    def start_background_loop(self, interval_minutes: int = None):
        """Starts fetching news in a background thread."""
        if interval_minutes is None:
            interval_minutes = config.NEWS_REFRESH_MINUTES

        self.__running = True
        self.__thread = threading.Thread(
            target=self.__loop,
            args=(interval_minutes * 60,),
            daemon=True
        )
        self.__thread.start()
        self._logger.info("News fetcher started")

    def stop(self):
        self.__running = False
        self._logger.info("News fetcher stopped")

    def __loop(self, interval_seconds: int):
        import time
        while self.__running:
            try:
                self.fetch_all_feeds()
            except Exception as e:
                self._handle_error(e, "Error in news fetch loop")
            time.sleep(interval_seconds)