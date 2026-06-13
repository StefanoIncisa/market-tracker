import customtkinter as ctk


class SectionHeader(ctk.CTkFrame):
    """
    Reusable section header with a divider line underneath.
    Used to separate asset categories in MarketsTab and PortfolioTab.
    Example: '⛽  COMMODITIES', '📊  ETFs'
    """

    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.__title = title
        self._setup_ui()

    def _setup_ui(self):
        # Section title
        ctk.CTkLabel(
            self,
            text=self.__title,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(fill="x", padx=5, pady=(15, 3))

        # Divider line
        ctk.CTkFrame(
            self,
            height=1,
            fg_color="gray30"
        ).pack(fill="x", padx=5, pady=(0, 5))