import customtkinter as ctk
from tracker.gui.base_tab import BaseTab
from tracker.gui.components import NewsCard


class NewsTab(BaseTab):
    """
    Displays AI-summarised financial news.
    Articles are rendered as cards with sentiment, summary, and portfolio impact.
    """

    def _setup_ui(self):
        # Top bar — filter buttons
        self._filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._filter_frame.pack(fill="x", padx=15, pady=(10, 0))

        ctk.CTkLabel(
            self._filter_frame,
            text="Filter:",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(side="left", padx=(0, 10))

        self._filter = ctk.StringVar(value="all")

        for label, value in [("All", "all"), ("🟢 Positive", "positive"),
                              ("🔴 Negative", "negative"), ("🟡 Neutral", "neutral")]:
            ctk.CTkRadioButton(
                self._filter_frame,
                text=label,
                variable=self._filter,
                value=value,
                font=ctk.CTkFont(size=12),
                command=self._on_filter_change
            ).pack(side="left", padx=10)

        # Scrollable article list
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=10, pady=10)

        self._articles = []
        self.show_loading("Fetching latest news...")

    def refresh(self, articles: list):
        """
        Called by the controller when new articles arrive.
        articles: list of NewsArticle objects
        """
        self.hide_loading()
        self._articles = articles
        self._render(articles)

    def _render(self, articles: list):
        """Protected — renders article cards into the scroll frame."""
        self._clear()

        if not articles:
            ctk.CTkLabel(
                self._scroll,
                text="No news articles yet. Fetching...",
                font=ctk.CTkFont(size=13),
                text_color="gray"
            ).pack(pady=40)
            return

        for article in articles:
            NewsCard(self._scroll, article).pack(
                fill="x", padx=5, pady=6
            )

    def _on_filter_change(self):
        """Protected — filters articles by sentiment when filter buttons are clicked."""
        value = self._filter.get()
        if value == "all":
            self._render(self._articles)
        else:
            filtered = [a for a in self._articles if a.sentiment == value]
            self._render(filtered)

    def _clear(self):
        for widget in self._scroll.winfo_children():
            widget.destroy()