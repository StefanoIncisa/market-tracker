import customtkinter as ctk


class StatCard(ctk.CTkFrame):
    """
    Reusable card displaying a single statistic.
    Used in PortfolioTab to show total value, daily P&L, total P&L etc.
    Example: 
    ┌─────────────────┐
    │ Total Value     │
    │ $12,450.00      │
    │ ▲ 2.3% today   │
    └─────────────────┘
    """

    def __init__(self, parent, title: str, value: str, subtitle: str = "", 
                 value_color: str = None, **kwargs):
        super().__init__(parent, corner_radius=10, **kwargs)
        self.__title = title
        self.__value = value
        self.__subtitle = subtitle
        self.__value_color = value_color
        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            self,
            text=self.__title,
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        ).grid(row=0, column=0, padx=15, pady=(12, 0), sticky="w")

        # Main value
        ctk.CTkLabel(
            self,
            text=self.__value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.__value_color or "white",
            anchor="w"
        ).grid(row=1, column=0, padx=15, pady=(2, 0), sticky="w")

        # Subtitle
        if self.__subtitle:
            ctk.CTkLabel(
                self,
                text=self.__subtitle,
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            ).grid(row=2, column=0, padx=15, pady=(2, 12), sticky="w")
        else:
            ctk.CTkLabel(self, text="").grid(row=2, column=0, pady=(0, 8))

    def update(self, value: str, subtitle: str = "", value_color: str = None):
        """Updates the card with new values without rebuilding."""
        self.__value = value
        self.__subtitle = subtitle
        self.__value_color = value_color
        for widget in self.winfo_children():
            widget.destroy()
        self._setup_ui()