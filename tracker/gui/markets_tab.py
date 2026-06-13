import customtkinter as ctk
from tracker.gui.base_tab import BaseTab
from tracker.gui.components import ColumnHeader, SectionHeader


class MarketsTab(BaseTab):
    """
    Displays live prices for all tracked assets.
    Works with plain PriceData objects — no database dependency.
    """

    CATEGORIES = ["commodity", "etf", "stock", "crypto"]
    CATEGORY_LABELS = {
        "commodity": "⛽  COMMODITIES",
        "etf":       "📊  ETFs",
        "stock":     "🏢  STOCKS",
        "crypto":    "₿   CRYPTO",
    }
    COLUMNS = [
        ("ASSET",   200, "w"),
        ("TICKER",  100, "w"),
        ("PRICE",   120, "e"),
        ("CHANGE",  100, "e"),
        ("VOLUME",  120, "e"),
    ]

    def _setup_ui(self):
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=10, pady=10)
        ColumnHeader(self._scroll, self.COLUMNS).pack(fill="x", padx=5, pady=(0, 5))
        self._price_rows = {}
        self.show_loading("Fetching live prices...")

    def refresh(self, data: dict):
        """data: {symbol: PriceData}"""
        self.hide_loading()
        self._clear()

        grouped = {}
        for symbol, price_data in data.items():
            grouped.setdefault(price_data.category, []).append((symbol, price_data))

        for category in self.CATEGORIES:
            if category not in grouped:
                continue
            SectionHeader(
                self._scroll,
                self.CATEGORY_LABELS.get(category, category.upper())
            ).pack(fill="x", padx=5)

            for symbol, price_data in grouped[category]:
                self._build_row(symbol, price_data)

    def _build_row(self, symbol: str, price_data):
        """Protected — builds a single price row from plain PriceData."""
        row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=2)

        is_positive = price_data.change_pct >= 0
        change_color = "#00C851" if is_positive else "#FF4444"
        arrow = "▲" if is_positive else "▼"

        ctk.CTkLabel(row, text=price_data.name, font=ctk.CTkFont(size=13),
                     width=200, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(row, text=symbol, font=ctk.CTkFont(size=12),
                     text_color="gray", width=100, anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(row, text=f"${price_data.price:,.2f}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     width=120, anchor="e").pack(side="left", padx=5)
        ctk.CTkLabel(row, text=f"{arrow} {abs(price_data.change_pct):.2f}%",
                     font=ctk.CTkFont(size=13), text_color=change_color,
                     width=100, anchor="e").pack(side="left", padx=5)
        ctk.CTkLabel(row, text=self._format_volume(price_data.volume),
                     font=ctk.CTkFont(size=12), text_color="gray",
                     width=120, anchor="e").pack(side="left", padx=5)

        self._price_rows[symbol] = row

    def _format_volume(self, volume) -> str:
        if not volume:
            return "—"
        if volume >= 1_000_000:
            return f"{volume / 1_000_000:.1f}M"
        if volume >= 1_000:
            return f"{volume / 1_000:.1f}K"
        return str(int(volume))

    def _clear(self):
        for widget in self._scroll.winfo_children():
            widget.destroy()
        self._price_rows = {}
        ColumnHeader(self._scroll, self.COLUMNS).pack(fill="x", padx=5, pady=(0, 5))