import customtkinter as ctk
from tracker.gui.base_tab import BaseTab
from tracker.gui.components import ColumnHeader, StatCard


class PortfolioTab(BaseTab):
    """
    Displays portfolio holdings and P&L.
    All calculations come from PortfolioService — this tab only renders.
    """

    COLUMNS = [
        ("ASSET",     200, "w"),
        ("TICKER",    100, "w"),
        ("QTY",        80, "e"),
        ("BUY PRICE", 120, "e"),
        ("NOW",       120, "e"),
        ("P&L",       120, "e"),
        ("P&L %",     100, "e"),
    ]

    def _setup_ui(self):
        # Stat cards row
        self._stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._stats_frame.pack(fill="x", padx=15, pady=(15, 5))

        self._card_total = StatCard(self._stats_frame, title="Total Value", value="—")
        self._card_total.pack(side="left", padx=(0, 10), ipadx=10)

        self._card_pnl = StatCard(self._stats_frame, title="Total P&L", value="—")
        self._card_pnl.pack(side="left", padx=(0, 10), ipadx=10)

        self._card_today = StatCard(self._stats_frame, title="Today's Change", value="—")
        self._card_today.pack(side="left", ipadx=10)

        # Holdings table
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=10, pady=10)
        ColumnHeader(self._scroll, self.COLUMNS).pack(fill="x", padx=5, pady=(0, 5))

        self.show_loading("Loading portfolio...")

    def refresh(self, positions: list, summary: dict):
        """
        positions: list of dicts from PortfolioService.get_position_data()
        summary: dict from PortfolioService.get_summary()
        """
        self.hide_loading()
        self._clear()

        if not positions:
            ctk.CTkLabel(
                self._scroll,
                text="No holdings yet. Add your first position.",
                font=ctk.CTkFont(size=13),
                text_color="gray"
            ).pack(pady=40)
            return

        for position in positions:
            self._build_row(position)

        self._update_cards(summary)

    def _build_row(self, position: dict):
        """Protected — renders a single holding row from pre-calculated data."""
        row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=2)

        pnl_color = "#00C851" if position["pnl"] >= 0 else "#FF4444"
        arrow = "▲" if position["pnl"] >= 0 else "▼"
        holding = position["holding"]
        snapshot = position["snapshot"]

        values = [
            (holding.asset.name,                    200, "w", None),
            (holding.asset.symbol,                  100, "w", "gray"),
            (f"{holding.quantity:,.4f}",             80, "e", None),
            (f"${holding.average_buy_price:,.2f}",  120, "e", None),
            (f"${snapshot.price:,.2f}",             120, "e", None),
            (f"{arrow} ${abs(position['pnl']):,.2f}", 120, "e", pnl_color),
            (f"{arrow} {abs(position['pnl_pct']):.2f}%", 100, "e", pnl_color),
        ]

        for text, width, anchor, color in values:
            ctk.CTkLabel(
                row,
                text=text,
                font=ctk.CTkFont(size=13),
                text_color=color or "white",
                width=width,
                anchor=anchor
            ).pack(side="left", padx=5)

    def _update_cards(self, summary: dict):
        """Protected — updates the stat cards with summary data."""
        pnl_color = "#00C851" if summary["total_pnl"] >= 0 else "#FF4444"
        today_color = "#00C851" if summary["total_today"] >= 0 else "#FF4444"

        self._card_total.update(
            value=f"${summary['total_current']:,.2f}",
            subtitle=f"Invested: ${summary['total_invested']:,.2f}"
        )
        self._card_pnl.update(
            value=f"${summary['total_pnl']:+,.2f}",
            subtitle=f"{summary['total_pnl_pct']:+.2f}% overall",
            value_color=pnl_color
        )
        self._card_today.update(
            value=f"${summary['total_today']:+,.2f}",
            subtitle="vs yesterday's close",
            value_color=today_color
        )

    def _clear(self):
        for widget in self._scroll.winfo_children():
            widget.destroy()
        ColumnHeader(self._scroll, self.COLUMNS).pack(fill="x", padx=5, pady=(0, 5))