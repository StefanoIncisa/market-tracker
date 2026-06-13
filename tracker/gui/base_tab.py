import customtkinter as ctk


class BaseTab(ctk.CTkFrame):
    """
    Parent class for all tabs in the app.
    Every tab inherits shared behaviour:
    - Loading state
    - Error display
    - Refresh mechanism
    - Consistent styling
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._is_loading = False
        self._setup_ui()

    def _setup_ui(self):
        """
        Protected — each tab overrides this to build its own UI.
        Called automatically on initialisation.
        """
        raise NotImplementedError("Each tab must implement _setup_ui()")

    def refresh(self, data=None):
        """
        Public — called by the controller when new data arrives.
        Each tab overrides this to update its display.
        """
        raise NotImplementedError("Each tab must implement refresh()")

    def show_loading(self, message: str = "Loading..."):
        """Shows a loading state on the tab."""
        self._is_loading = True
        self._loading_label = ctk.CTkLabel(
            self,
            text=message,
            font=ctk.CTkFont(size=14)
        )
        self._loading_label.place(relx=0.5, rely=0.5, anchor="center")

    def hide_loading(self):
        """Hides the loading state."""
        self._is_loading = False
        if hasattr(self, "_loading_label"):
            self._loading_label.destroy()

    def show_error(self, message: str):
        """Shows an error message on the tab."""
        self.hide_loading()
        error_label = ctk.CTkLabel(
            self,
            text=f"⚠ {message}",
            font=ctk.CTkFont(size=13),
            text_color="#FF5555"
        )
        error_label.place(relx=0.5, rely=0.5, anchor="center")

    def _make_header(self, text: str) -> ctk.CTkLabel:
        """
        Protected helper — creates a consistent section header.
        """
        label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        return label

    def _make_subheader(self, text: str) -> ctk.CTkLabel:
        """
        Protected helper — creates a consistent subheader.
        """
        label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        return label