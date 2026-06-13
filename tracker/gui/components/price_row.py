import customtkinter as ctk


class PriceRow(ctk.CTkFrame):
    """
    Reusable row displaying a single asset's price data.
    Used in both MarketsTab and PortfolioTab.
    Shows: asset name, ticker, price, change %, and optional volume.
    """

    def __init__(self, parent, snapshot, show_volume: bool = True, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.__snapshot = snapshot
        self.__show_volume = show_volume
        self._setup_ui()

    def _setup_ui(self):
        snapshot = self.__snapshot
        is_positive = snapshot.change_pct >= 0
        change_color = "#00C851" if is_positive else "#FF4444"
        arrow = "▲" if is_positive else "▼"

        # Asset name
        ctk.CTkLabel(
            self,
            text=snapshot.asset.name,
            font=ctk.CTkFont(size=13),
            width=200,
            anchor="w"
        ).pack(side="left", padx=5)

        # Ticker symbol
        ctk.CTkLabel(
            self,
            text=snapshot.asset.symbol,
            font=ctk.CTkFont(size=12),
            text_color="gray",
            width=100,
            anchor="w"
        ).pack(side="left", padx=5)

        # Price
        ctk.CTkLabel(
            self,
            text=f"${snapshot.price:,.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120,
            anchor="e"
        ).pack(side="left", padx=5)

        # Change %
        ctk.CTkLabel(
            self,
            text=f"{arrow} {abs(snapshot.change_pct):.2f}%",
            font=ctk.CTkFont(size=13),
            text_color=change_color,
            width=100,
            anchor="e"
        ).pack(side="left", padx=5)

        # Volume — optional
        if self.__show_volume:
            ctk.CTkLabel(
                self,
                text=self._format_volume(snapshot.volume),
                font=ctk.CTkFont(size=12),
                text_color="gray",
                width=120,
                anchor="e"
            ).pack(side="left", padx=5)

    def _format_volume(self, volume) -> str:
        """Protected — formats volume into a readable string."""
        if not volume:
            return "—"
        if volume >= 1_000_000:
            return f"{volume / 1_000_000:.1f}M"
        if volume >= 1_000:
            return f"{volume / 1_000:.1f}K"
        return str(int(volume))

    def update_data(self, snapshot):
        """Updates the row with new price data without rebuilding the whole UI."""
        self.__snapshot = snapshot
        for widget in self.winfo_children():
            widget.destroy()
        self._setup_ui()