from textual.app import ComposeResult
from textual.containers import Container, HorizontalGroup, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Select, Static, Switch


class SettingsScreen(Screen):
    """Settings configuration screen"""
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("ctrl+s", "save_settings", "Save Settings"),
    ]
    
    def __init__(self):
        super().__init__()
        self.settings = {
            "model": "groq/mixtral-8x7b-32768",
            "api_key": "",
            "temperature": 0.7,
            "max_tokens": 4096,
            "dark_mode": True,
            "auto_save": True,
        }
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("[bold green]Settings Configuration[/bold green]", classes="title"),
            Vertical(
                Label("Model Provider:"),
                Select([
                    ("Groq - Mixtral 8x7B", "groq/mixtral-8x7b-32768"),
                    ("Groq - Llama 3.1", "groq/llama-3.1-70b-versatile"),
                    ("OpenAI - GPT-4", "openai/gpt-4"),
                    ("Anthropic - Claude", "anthropic/claude-3-sonnet"),
                ], value=self.settings["model"], id="model_select"),
                
                Label("API Key:"),
                Input(
                    placeholder="Enter your API key...", 
                    password=True,
                    value=self.settings["api_key"],
                    id="api_key_input"
                ),
                
                Label("Temperature:"),
                Input(
                    placeholder="0.0 - 1.0", 
                    value=str(self.settings["temperature"]),
                    id="temperature_input"
                ),
                
                Label("Max Tokens:"),
                Input(
                    placeholder="1024 - 8192", 
                    value=str(self.settings["max_tokens"]),
                    id="max_tokens_input"
                ),
                
                HorizontalGroup(
                    Label("Dark Mode:"),
                    Switch(value=self.settings["dark_mode"], id="dark_mode_switch"),
                ),
                
                HorizontalGroup(
                    Label("Auto Save:"),
                    Switch(value=self.settings["auto_save"], id="auto_save_switch"),
                ),
                
                HorizontalGroup(
                    Button("Save Settings", variant="primary", id="save_button"),
                    Button("Reset to Defaults", variant="error", id="reset_button"),
                    Button("Back", variant="default", id="back_button"),
                ),
                classes="settings-form"
            ),
            id="settings_container"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_button":
            self.save_settings()
        elif event.button.id == "reset_button":
            self.reset_settings()
        elif event.button.id == "back_button":
            self.app.pop_screen()
    
    def save_settings(self) -> None:
        # Collect settings from form
        model_select = self.query_one("#model_select", Select)
        api_key_input = self.query_one("#api_key_input", Input)
        temperature_input = self.query_one("#temperature_input", Input)
        max_tokens_input = self.query_one("#max_tokens_input", Input)
        dark_mode_switch = self.query_one("#dark_mode_switch", Switch)
        auto_save_switch = self.query_one("#auto_save_switch", Switch)
        
        self.settings.update({
            "model": model_select.value,
            "api_key": api_key_input.value,
            "temperature": float(temperature_input.value) if temperature_input.value else 0.7,
            "max_tokens": int(max_tokens_input.value) if max_tokens_input.value else 4096,
            "dark_mode": dark_mode_switch.value,
            "auto_save": auto_save_switch.value,
        })
        
        self.notify("Settings saved successfully!", severity="information")
        self.app.pop_screen()
    
    def reset_settings(self) -> None:
        self.settings = {
            "model": "groq/mixtral-8x7b-32768",
            "api_key": "",
            "temperature": 0.7,
            "max_tokens": 4096,
            "dark_mode": True,
            "auto_save": True,
        }
        self.notify("Settings reset to defaults!", severity="information")
        self.refresh()
