import customtkinter as ctk


class ChatBubble(ctk.CTkFrame):
    """
    Reusable chat bubble for the AI Analyst tab.
    Displays a single message from either the user or the AI.
    User messages align right, AI messages align left.
    """

    USER_COLOR = "#1F6AA5"
    AI_COLOR   = "gray20"
    USER_LABEL = "You"
    AI_LABEL   = "AI Analyst"

    def __init__(self, parent, message: str, role: str, timestamp: str = "", **kwargs):
        """
        role: "user" | "assistant"
        """
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.__message = message
        self.__role = role
        self.__timestamp = timestamp
        self._setup_ui()

    def _setup_ui(self):
        is_user = self.__role == "user"

        # Outer alignment frame
        align_frame = ctk.CTkFrame(self, fg_color="transparent")
        align_frame.pack(fill="x", padx=10, pady=4)

        # Bubble frame
        bubble = ctk.CTkFrame(
            align_frame,
            fg_color=self.USER_COLOR if is_user else self.AI_COLOR,
            corner_radius=12
        )

        # Sender label
        sender_label = ctk.CTkLabel(
            bubble,
            text=self.USER_LABEL if is_user else self.AI_LABEL,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="gray70"
        )
        sender_label.pack(anchor="w", padx=12, pady=(8, 0))

        # Message text
        ctk.CTkLabel(
            bubble,
            text=self.__message,
            font=ctk.CTkFont(size=13),
            anchor="w",
            justify="left",
            wraplength=500
        ).pack(anchor="w", padx=12, pady=(4, 0))

        # Timestamp
        if self.__timestamp:
            ctk.CTkLabel(
                bubble,
                text=self.__timestamp,
                font=ctk.CTkFont(size=10),
                text_color="gray50"
            ).pack(anchor="e", padx=12, pady=(2, 8))
        else:
            ctk.CTkLabel(bubble, text="").pack(pady=(0, 6))

        # Align bubble to right for user, left for AI
        if is_user:
            bubble.pack(anchor="e", padx=(80, 0))
        else:
            bubble.pack(anchor="w", padx=(0, 80))