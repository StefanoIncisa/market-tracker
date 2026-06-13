import customtkinter as ctk


class AlertRow(ctk.CTkFrame):
    """
    Reusable row displaying a single alert.
    Used in AlertsTab.
    Shows: asset, condition, threshold, status, and a toggle button.
    """

    def __init__(self, parent, alert, on_toggle=None, on_delete=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.__alert = alert
        self.__on_toggle = on_toggle
        self.__on_delete = on_delete
        self._setup_ui()

    def _setup_ui(self):
        alert = self.__alert

        # Status indicator
        status_color = "#00C851" if alert.active else "gray"
        ctk.CTkLabel(
            self,
            text="●",
            font=ctk.CTkFont(size=14),
            text_color=status_color,
            width=20
        ).pack(side="left", padx=(5, 10))

        # Asset symbol
        ctk.CTkLabel(
            self,
            text=alert.asset.symbol,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=100,
            anchor="w"
        ).pack(side="left", padx=5)

        # Condition
        condition_text = self._format_condition(alert)
        ctk.CTkLabel(
            self,
            text=condition_text,
            font=ctk.CTkFont(size=13),
            width=200,
            anchor="w"
        ).pack(side="left", padx=5)

        # Status label
        status_text = "Active" if alert.active else "Inactive"
        ctk.CTkLabel(
            self,
            text=status_text,
            font=ctk.CTkFont(size=12),
            text_color=status_color,
            width=80,
            anchor="w"
        ).pack(side="left", padx=5)

        # Toggle button
        toggle_text = "Disable" if alert.active else "Enable"
        ctk.CTkButton(
            self,
            text=toggle_text,
            font=ctk.CTkFont(size=12),
            width=80,
            height=28,
            command=self.__handle_toggle
        ).pack(side="left", padx=5)

        # Delete button
        ctk.CTkButton(
            self,
            text="Delete",
            font=ctk.CTkFont(size=12),
            width=70,
            height=28,
            fg_color="#FF4444",
            hover_color="#CC0000",
            command=self.__handle_delete
        ).pack(side="left", padx=5)

    def _format_condition(self, alert) -> str:
        """Protected — formats the alert condition into readable text."""
        if alert.condition == "above":
            return f"Price above ${alert.threshold:,.2f}"
        elif alert.condition == "below":
            return f"Price below ${alert.threshold:,.2f}"
        elif alert.condition == "change_pct":
            return f"Change exceeds ±{alert.threshold:.1f}%"
        return f"{alert.condition} {alert.threshold}"

    def __handle_toggle(self):
        """Private — calls the toggle callback passed in from the tab."""
        if self.__on_toggle:
            self.__on_toggle(self.__alert)

    def __handle_delete(self):
        """Private — calls the delete callback passed in from the tab."""
        if self.__on_delete:
            self.__on_delete(self.__alert)