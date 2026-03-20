
from textual.app import App

from .main_screen import MainScreen


class AnonymousCoderApp(App):
    """A Textual app for coding through CLI"""

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+d", "toggle_dark", "Toggle Dark Mode"),
    ]
    
    CSS_PATH = "app.tcss"

    def __init__(self, graph=None, config=None, database=None, **kwargs):
        super().__init__(**kwargs)
        self.graph = graph
        self.agent_config = config
        self.database = database

    def on_mount(self) -> None:
        """Called when app starts."""
        main_screen = MainScreen(
            graph=self.graph,
            config=self.agent_config,
            database=self.database
        )
        self.install_screen(main_screen, name="main")
        self.push_screen("main")

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark


if __name__ == "__main__":
    app = AnonymousCoderApp()
    app.run()