import customtkinter as ctk
from tracker.gui.base_tab import BaseTab
from tracker.gui.markets_tab import MarketsTab
from tracker.gui.portfolio_tab import PortfolioTab
from tracker.gui.news_tab import NewsTab
from tracker.gui.analyst_tab import AnalystTab
from tracker.gui.alerts_tab import AlertsTab


# Global appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class GUIApp(ctk.CTk):
    """
    Main application window.
    Boots all tabs and provides methods for the controller to push data updates.
    Never fetches data itself — that's the controller's job.
    """

    TITLE = "📈 Market Tracker"
    WIDTH = 1100
    HEIGHT = 720

    def __init__(self):
        super().__init__()
        self.title(self.TITLE)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(900, 600)
        self._setup_ui()

    def _setup_ui(self):
        """Builds the main window layout with a tab view."""

        # Tab view
        self._tabs = ctk.CTkTabview(self, anchor="nw")
        self._tabs.pack(fill="both", expand=True, padx=10, pady=10)

        # Create all tabs
        self._tabs.add("📈  Markets")
        self._tabs.add("📁  Portfolio")
        self._tabs.add("📰  News")
        self._tabs.add("🤖  AI Analyst")
        self._tabs.add("🚨  Alerts")

        # Instantiate tab classes inside each tab frame
        self.markets_tab = MarketsTab(
            self._tabs.tab("📈  Markets")
        )
        self.markets_tab.pack(fill="both", expand=True)

        self.portfolio_tab = PortfolioTab(
            self._tabs.tab("📁  Portfolio")
        )
        self.portfolio_tab.pack(fill="both", expand=True)

        self.news_tab = NewsTab(
            self._tabs.tab("📰  News")
        )
        self.news_tab.pack(fill="both", expand=True)

        self.analyst_tab = AnalystTab(
            self._tabs.tab("🤖  AI Analyst")
        )
        self.analyst_tab.pack(fill="both", expand=True)

        self.alerts_tab = AlertsTab(
            self._tabs.tab("🚨  Alerts")
        )
        self.alerts_tab.pack(fill="both", expand=True)

    # ── Public update methods — called by the controller ──────────────────────

    def update_prices(self, price_data: dict):
        """Pushes new price data to the markets tab."""
        self.markets_tab.refresh(price_data)

    def update_portfolio(self, positions: list, summary: dict):
        """Pushes updated portfolio data to the portfolio tab."""
        self.portfolio_tab.refresh(positions, summary)

    def update_news(self, articles: list):
        """Pushes new articles to the news tab."""
        self.news_tab.refresh(articles)

    def update_analyst_context(self, price_data: dict, holdings: list, news: list):
        """Keeps the analyst tab's context current."""
        self.analyst_tab.set_context(price_data, holdings, news)

    def update_daily_summary(self, summary: str):
        """Updates the daily briefing in the analyst tab."""
        self.analyst_tab.update_summary(summary)

    def update_alerts(self, alerts: list):
        """Pushes updated alerts list to the alerts tab."""
        self.alerts_tab.refresh(alerts)

    def show_alert_notification(self, alert, log):
        """Shows a popup notification when an alert fires."""
        symbol = alert.asset.symbol
        condition = alert.condition
        price = log.price_at_trigger

        ctk.CTkToplevel(self).after(100, lambda: self._alert_popup(
            f"🚨 Alert triggered: {symbol} {condition} ${price:,.2f}"
        ))

    def _alert_popup(self, message: str):
        """Private — renders the alert notification popup."""
        popup = ctk.CTkToplevel(self)
        popup.title("Alert Triggered")
        popup.geometry("400x120")
        popup.resizable(False, False)

        ctk.CTkLabel(
            popup,
            text=message,
            font=ctk.CTkFont(size=13),
            wraplength=360
        ).pack(pady=20, padx=20)

        ctk.CTkButton(
            popup,
            text="Dismiss",
            width=100,
            command=popup.destroy
        ).pack(pady=(0, 15))