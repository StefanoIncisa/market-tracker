import customtkinter as ctk
import webbrowser


class NewsCard(ctk.CTkFrame):
    """
    Reusable card displaying a news article with AI summary.
    Used in NewsTab.
    Shows: sentiment, source, title, AI summary, affected assets, and a link.
    """

    def __init__(self, parent, article, **kwargs):
        super().__init__(parent, corner_radius=10, **kwargs)
        self.__article = article
        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        article = self.__article

        # Top row — sentiment emoji + source + date
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.grid(row=0, column=0, padx=15, pady=(12, 0), sticky="ew")

        ctk.CTkLabel(
            top_row,
            text=article.sentiment_emoji,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            top_row,
            text=article.source,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="gray"
        ).pack(side="left")

        if article.published_at:
            date_str = article.published_at.strftime("%d %b %Y %H:%M")
            ctk.CTkLabel(
                top_row,
                text=date_str,
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack(side="right")

        # Title
        ctk.CTkLabel(
            self,
            text=article.title,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            wraplength=600,
            justify="left"
        ).grid(row=1, column=0, padx=15, pady=(6, 0), sticky="w")

        # AI Summary
        if article.summary:
            ctk.CTkLabel(
                self,
                text=article.summary,
                font=ctk.CTkFont(size=12),
                text_color="gray",
                anchor="w",
                wraplength=600,
                justify="left"
            ).grid(row=2, column=0, padx=15, pady=(6, 0), sticky="w")

        # Impact analysis
        if article.impact_analysis:
            ctk.CTkLabel(
                self,
                text=f"💼 {article.impact_analysis}",
                font=ctk.CTkFont(size=12),
                text_color="#4A9EFF",
                anchor="w",
                wraplength=600,
                justify="left"
            ).grid(row=3, column=0, padx=15, pady=(6, 0), sticky="w")

        # Affected assets tags
        if article.affected_assets:
            tags_row = ctk.CTkFrame(self, fg_color="transparent")
            tags_row.grid(row=4, column=0, padx=15, pady=(8, 0), sticky="w")

            ctk.CTkLabel(
                tags_row,
                text="Affects:",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack(side="left", padx=(0, 6))

            for symbol in article.affected_assets:
                ctk.CTkLabel(
                    tags_row,
                    text=symbol,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    fg_color="gray25",
                    corner_radius=4,
                    padx=6,
                    pady=2
                ).pack(side="left", padx=3)

        # Read more link
        link = ctk.CTkButton(
            self,
            text="Read full article →",
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            text_color="#4A9EFF",
            hover=False,
            anchor="w",
            command=self.__open_link
        )
        link.grid(row=5, column=0, padx=12, pady=(6, 12), sticky="w")

    def __open_link(self):
        """Private — opens the article URL in the default browser."""
        if self.__article.url:
            webbrowser.open(self.__article.url)
            