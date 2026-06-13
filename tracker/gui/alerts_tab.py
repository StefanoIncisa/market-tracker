import customtkinter as ctk
from tracker.gui.base_tab import BaseTab
from tracker.gui.components import ColumnHeader, AlertRow


class AlertsTab(BaseTab):
    """
    Displays and manages price alerts.
    Users can create, toggle, and delete alerts.
    Shows a log of recently triggered alerts.
    """

    COLUMNS = [
        ("",          20,  "w"),
        ("ASSET",     100, "w"),
        ("CONDITION", 200, "w"),
        ("STATUS",    80,  "w"),
        ("",          80,  "w"),
        ("",          70,  "w"),
    ]

    def _setup_ui(self):
        # Create alert form at the top
        self._form_frame = ctk.CTkFrame(self, corner_radius=10)
        self._form_frame.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            self._form_frame,
            text="➕  New Alert",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(10, 6))

        # Form inputs row
        inputs_row = ctk.CTkFrame(self._form_frame, fg_color="transparent")
        inputs_row.pack(fill="x", padx=15, pady=(0, 12))

        # Symbol input
        self._symbol_input = ctk.CTkEntry(
            inputs_row,
            placeholder_text="Ticker (e.g. AAPL)",
            font=ctk.CTkFont(size=12),
            width=140,
            height=36
        )
        self._symbol_input.pack(side="left", padx=(0, 8))

        # Condition dropdown
        self._condition = ctk.StringVar(value="above")
        ctk.CTkOptionMenu(
            inputs_row,
            variable=self._condition,
            values=["above", "below", "change_pct"],
            font=ctk.CTkFont(size=12),
            width=130,
            height=36
        ).pack(side="left", padx=(0, 8))

        # Threshold input
        self._threshold_input = ctk.CTkEntry(
            inputs_row,
            placeholder_text="Value (e.g. 300)",
            font=ctk.CTkFont(size=12),
            width=140,
            height=36
        )
        self._threshold_input.pack(side="left", padx=(0, 8))

        # Create button
        ctk.CTkButton(
            inputs_row,
            text="Create Alert",
            font=ctk.CTkFont(size=12),
            width=120,
            height=36,
            command=self._on_create
        ).pack(side="left")

        # Error label
        self._error_label = ctk.CTkLabel(
            self._form_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#FF4444"
        )
        self._error_label.pack(anchor="w", padx=15, pady=(0, 8))

        # Active alerts list
        ctk.CTkLabel(
            self,
            text="Active Alerts",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(anchor="w", padx=20, pady=(10, 0))

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=10, pady=5)

        ColumnHeader(self._scroll, self.COLUMNS).pack(fill="x", padx=5, pady=(0, 5))

        self._on_create_callback = None
        self._on_toggle_callback = None
        self._on_delete_callback = None

        self.show_loading("Loading alerts...")

    def set_callbacks(self, on_create, on_toggle, on_delete):
        """Registers controller callbacks for alert actions."""
        self._on_create_callback = on_create
        self._on_toggle_callback = on_toggle
        self._on_delete_callback = on_delete

    def refresh(self, alerts: list):
        """Called by controller when alerts list updates."""
        self.hide_loading()
        self._clear()

        if not alerts:
            ctk.CTkLabel(
                self._scroll,
                text="No alerts yet. Create one above.",
                font=ctk.CTkFont(size=13),
                text_color="gray"
            ).pack(pady=40)
            return

        for alert in alerts:
            AlertRow(
                self._scroll,
                alert=alert,
                on_toggle=self._on_toggle_callback,
                on_delete=self._on_delete_callback
            ).pack(fill="x", padx=5, pady=2)

    def _on_create(self):
        """Protected — validates form and calls create callback."""
        symbol = self._symbol_input.get().strip().upper()
        condition = self._condition.get()
        threshold_raw = self._threshold_input.get().strip()

        if not symbol:
            self._show_error("Please enter a ticker symbol.")
            return

        try:
            threshold = float(threshold_raw)
        except ValueError:
            self._show_error("Threshold must be a number.")
            return

        self._error_label.configure(text="")

        if self._on_create_callback:
            self._on_create_callback(symbol, condition, threshold)

        self._symbol_input.delete(0, "end")
        self._threshold_input.delete(0, "end")

    def _show_error(self, message: str):
        """Protected — shows a validation error below the form."""
        self._error_label.configure(text=f"⚠ {message}")

    def _clear(self):
        for widget in self._scroll.winfo_children():
            widget.destroy()
        ColumnHeader(self._scroll, self.COLUMNS).pack(fill="x", padx=5, pady=(0, 5))