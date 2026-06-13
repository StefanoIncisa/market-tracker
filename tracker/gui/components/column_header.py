import customtkinter as ctk


class ColumnHeader(ctk.CTkFrame):
    """
    Reusable column header row for any table in the app.
    Accepts a list of column definitions and renders them consistently.
    Used by MarketsTab, PortfolioTab, and AlertsTab.
    """

    def __init__(self, parent, columns: list[tuple], **kwargs):
        """
        columns: list of (label, width, anchor) tuples
        Example: [("ASSET", 200, "w"), ("PRICE", 120, "e")]
        """
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.__columns = columns
        self._setup_ui()

    def _setup_ui(self):
        for text, width, anchor in self.__columns:
            ctk.CTkLabel(
                self,
                text=text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="gray",
                width=width,
                anchor=anchor
            ).pack(side="left", padx=5)