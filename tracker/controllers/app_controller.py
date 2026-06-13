import threading
from tracker.database import Database
from tracker.services import (
    PriceFetcherService,
    NewsFetcherService,
    AlertService,
    AIAnalystService,
    PortfolioService,
)
from tracker.repositories import (
    AlertRepository,
    NewsRepository,
)


class AppController:
    """
    Orchestrates all services and connects them to the GUI.
    The GUI never talks to services directly — everything goes through here.
    """

    def __init__(self, app):
        self.__app = app
        self.__db = Database()
        self.__price_data = {}
        self.__holdings = []
        self.__recent_news = []

        # Initialise services
        self.__price_fetcher = PriceFetcherService(
            on_update=self.__on_prices_updated
        )
        self.__news_fetcher = NewsFetcherService(
            on_update=self.__on_news_updated
        )
        self.__alert_service = AlertService(
            on_alert=self.__on_alert_triggered
        )
        self.__ai_service = AIAnalystService()
        self.__portfolio_service = PortfolioService()

        # Wire up GUI callbacks
        self.__app.analyst_tab.set_chat_callback(self.__on_chat)
        self.__app.alerts_tab.set_callbacks(
            on_create=self.__on_create_alert,
            on_toggle=self.__on_toggle_alert,
            on_delete=self.__on_delete_alert,
        )

    def start(self):
        """
        Starts all background services.
        Called once when the app launches.
        """
        # Initial data fetch before starting loops
        self.__price_fetcher.fetch_all()
        self.__news_fetcher.fetch_all_feeds()
        self.__refresh_portfolio()
        self.__refresh_alerts()
        self.__generate_daily_summary()

        # Start background loops
        self.__price_fetcher.start_background_loop()
        self.__news_fetcher.start_background_loop()

    def stop(self):
        """Stops all background services cleanly."""
        self.__price_fetcher.stop()
        self.__news_fetcher.stop()

    # ── Private callbacks — triggered by services ─────────────────────────────

    def __on_prices_updated(self, price_data: dict):
        """Called by PriceFetcherService when new prices arrive."""
        self.__price_data = price_data

        # Check alerts
        self.__alert_service.check_all(price_data)

        # Refresh portfolio
        self.__refresh_portfolio()

        # Update analyst context
        self.__app.update_analyst_context(
            self.__price_data,
            self.__holdings,
            self.__recent_news
        )

        # Push to GUI — must run on main thread
        self.__app.after(0, lambda: self.__app.update_prices(price_data))

    def __on_news_updated(self, new_articles: list):
        """Called by NewsFetcherService when new articles arrive."""
        # Analyse new articles with AI in background
        threading.Thread(
            target=self.__analyse_articles,
            args=(new_articles,),
            daemon=True
        ).start()

    def __on_alert_triggered(self, alert, log):
        """Called by AlertService when an alert fires."""
        self.__app.after(
            0, lambda: self.__app.show_alert_notification(alert, log)
        )
        self.__refresh_alerts()

    def __on_chat(self, message: str, price_data: dict, holdings: list, news: list):
        """Called by AnalystTab when user sends a message."""
        threading.Thread(
            target=self.__process_chat,
            args=(message, price_data, holdings, news),
            daemon=True
        ).start()

    # ── Private alert callbacks — triggered by GUI ────────────────────────────

    def __on_create_alert(self, symbol: str, condition: str, threshold: float):
        """Called by AlertsTab when user creates a new alert."""
        self.__alert_service.create_alert(symbol, condition, threshold)
        self.__refresh_alerts()

    def __on_toggle_alert(self, alert):
        """Called by AlertsTab when user toggles an alert."""
        session = self.__db.get_session()
        repo = AlertRepository(session)
        if alert.active:
            repo.deactivate(alert)
        else:
            repo.activate(alert)
        session.close()
        self.__refresh_alerts()

    def __on_delete_alert(self, alert):
        """Called by AlertsTab when user deletes an alert."""
        session = self.__db.get_session()
        repo = AlertRepository(session)
        repo.delete(alert)
        session.close()
        self.__refresh_alerts()

    # ── Private helpers ───────────────────────────────────────────────────────

    def __refresh_portfolio(self):
        """Recalculates portfolio and pushes to GUI."""
        self.__holdings = self.__portfolio_service.get_holdings()
        positions = [
            self.__portfolio_service.get_position_data(h, self.__price_data)
            for h in self.__holdings
        ]
        positions = [p for p in positions if p]
        summary = self.__portfolio_service.get_summary(self.__price_data)
        self.__app.after(
            0, lambda: self.__app.update_portfolio(positions, summary)
        )

    def __refresh_alerts(self):
        """Fetches latest alerts and pushes to GUI."""
        session = self.__db.get_session()
        repo = AlertRepository(session)
        alerts = repo.get_all()
        session.close()
        self.__app.after(0, lambda: self.__app.update_alerts(alerts))

    def __refresh_news(self):
        """Fetches latest analysed articles and pushes to GUI."""
        session = self.__db.get_session()
        repo = NewsRepository(session)
        articles = repo.get_analysed()
        self.__recent_news = articles
        session.close()
        self.__app.after(0, lambda: self.__app.update_news(articles))

    def __analyse_articles(self, articles: list):
        """Runs AI analysis on new articles in a background thread."""
        for article in articles:
            self.__ai_service.summarise_news(article)
        self.__refresh_news()

    def __generate_daily_summary(self):
        """Generates the morning briefing in a background thread."""
        threading.Thread(
            target=self.__run_daily_summary,
            daemon=True
        ).start()

    def __run_daily_summary(self):
        """Private — runs the daily summary generation."""
        session = self.__db.get_session()
        repo = NewsRepository(session)
        recent_news = repo.get_recent(limit=5)
        session.close()

        summary = self.__ai_service.daily_summary(self.__price_data, recent_news)
        self.__app.after(0, lambda: self.__app.update_daily_summary(summary))

    def __process_chat(self, message: str, price_data: dict, holdings: list, news: list):
        """Private — sends message to AI and returns response to GUI."""
        response = self.__ai_service.chat(message, price_data, holdings, news)
        self.__app.after(0, lambda: self.__app.analyst_tab.receive_response(response))