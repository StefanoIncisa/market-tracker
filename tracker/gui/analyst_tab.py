import customtkinter as ctk
from datetime import datetime
from tracker.gui.base_tab import BaseTab
from tracker.gui.components import ChatBubble


class AnalystTab(BaseTab):
    """
    AI chat interface — ask anything about your portfolio or the markets.
    Sends full context (prices, holdings, news) with every message.
    """

    def _setup_ui(self):
        # Daily summary bar at the top
        self._summary_frame = ctk.CTkFrame(self, corner_radius=10)
        self._summary_frame.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(
            self._summary_frame,
            text="📋  Daily Briefing",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(10, 4))

        self._summary_label = ctk.CTkLabel(
            self._summary_frame,
            text="Generating your daily briefing...",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
            wraplength=700,
            justify="left"
        )
        self._summary_label.pack(anchor="w", padx=15, pady=(0, 10))

        # Chat history
        self._chat_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._chat_scroll.pack(fill="both", expand=True, padx=10, pady=(5, 0))

        # Input row at the bottom
        self._input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._input_frame.pack(fill="x", padx=15, pady=10)

        self._input = ctk.CTkEntry(
            self._input_frame,
            placeholder_text="Ask anything — e.g. 'Why is gold up today?' or 'How is my portfolio doing?'",
            font=ctk.CTkFont(size=13),
            height=40
        )
        self._input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._input.bind("<Return>", self._on_send)

        self._send_btn = ctk.CTkButton(
            self._input_frame,
            text="Send",
            font=ctk.CTkFont(size=13),
            width=80,
            height=40,
            command=self._on_send
        )
        self._send_btn.pack(side="left")

        # Internal state
        self._on_chat_callback = None
        self._price_data = {}
        self._holdings = []
        self._recent_news = []

    def set_context(self, price_data: dict, holdings: list, recent_news: list):
        """
        Called by the controller to keep the tab's context up to date.
        Every message sent to the AI includes this context.
        """
        self._price_data = price_data
        self._holdings = holdings
        self._recent_news = recent_news

    def set_chat_callback(self, callback):
        """Registers the function to call when user sends a message."""
        self._on_chat_callback = callback

    def refresh(self, data=None):
        """Called by controller — no-op here, context is set via set_context."""
        pass

    def update_summary(self, summary: str):
        """Updates the daily briefing text at the top."""
        self._summary_label.configure(text=summary)

    def add_message(self, message: str, role: str):
        """Adds a chat bubble to the conversation."""
        timestamp = datetime.now().strftime("%H:%M")
        bubble = ChatBubble(
            self._chat_scroll,
            message=message,
            role=role,
            timestamp=timestamp
        )
        bubble.pack(fill="x", pady=2)
        self._chat_scroll._parent_canvas.yview_moveto(1.0)

    def _on_send(self, event=None):
        """Protected — handles send button click and Enter key."""
        message = self._input.get().strip()
        if not message:
            return

        self._input.delete(0, "end")
        self.add_message(message, "user")
        self._set_loading(True)

        if self._on_chat_callback:
            self._on_chat_callback(
                message,
                self._price_data,
                self._holdings,
                self._recent_news
            )

    def receive_response(self, response: str):
        """Called by the controller when the AI response is ready."""
        self._set_loading(False)
        self.add_message(response, "assistant")

    def _set_loading(self, loading: bool):
        """Protected — disables input while waiting for AI response."""
        state = "disabled" if loading else "normal"
        self._send_btn.configure(state=state)
        self._input.configure(state=state)