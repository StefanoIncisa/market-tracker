import logging
from tracker.database import Database
from tracker.gui.app import GUIApp
from tracker.controllers.app_controller import AppController


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)


def main():
    # Initialise database and seed default assets
    db = Database()
    Database.seed_assets()

    # Boot the GUI
    app = GUIApp()

    # Boot the controller — wires services to GUI
    controller = AppController(app)

    # Stop services cleanly when window is closed
    app.protocol("WM_DELETE_WINDOW", lambda: _on_close(app, controller))

    # Start all background services
    controller.start()

    # Start the GUI event loop — this blocks until window is closed
    app.mainloop()


def _on_close(app, controller):
    """Stops all services before closing the window."""
    controller.stop()
    app.destroy()


if __name__ == "__main__":
    main()