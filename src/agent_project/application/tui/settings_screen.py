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
            "model": "anthropic.claude-3-sonnet-20240229-v1:0",
            "aws_region": "us-east-1",
            "temperature": 0.7,
            "max_tokens": 4096,
            "dark_mode": True,
            "auto_save": True,
        }
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("[bold green]Settings Configuration[/bold green]", classes="title"),
            Vertical(
                Label("Bedrock Model:"),
                Select([
                    ("Claude 3 Sonnet", "anthropic.claude-3-sonnet-20240229-v1:0"),
                    ("Claude 3 Haiku", "anthropic.claude-3-haiku-20240307-v1:0"),
                    ("Claude 3.5 Sonnet", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
                    ("Llama 3 70B Instruct", "meta.llama3-70b-instruct-v1:0"),
                ], value=self.settings["model"], id="model_select"),
                
                Label("AWS Region:"),
                Input(
                    placeholder="e.g. us-east-1",
                    value=self.settings["aws_region"],
                    id="aws_region_input"
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
        aws_region_input = self.query_one("#aws_region_input", Input)
        temperature_input = self.query_one("#temperature_input", Input)
        max_tokens_input = self.query_one("#max_tokens_input", Input)
        dark_mode_switch = self.query_one("#dark_mode_switch", Switch)
        auto_save_switch = self.query_one("#auto_save_switch", Switch)
        
        self.settings.update({
            "model": model_select.value,
            "aws_region": aws_region_input.value if aws_region_input.value else "us-east-1",
            "temperature": float(temperature_input.value) if temperature_input.value else 0.7,
            "max_tokens": int(max_tokens_input.value) if max_tokens_input.value else 4096,
            "dark_mode": dark_mode_switch.value,
            "auto_save": auto_save_switch.value,
        })
        
        self.notify("Settings saved successfully!", severity="information")
        self.app.pop_screen()
    
    def reset_settings(self) -> None:
        self.settings = {
            "model": "anthropic.claude-3-sonnet-20240229-v1:0",
            "aws_region": "us-east-1",
            "temperature": 0.7,
            "max_tokens": 4096,
            "dark_mode": True,
            "auto_save": True,
        }
        self.notify("Settings reset to defaults!", severity="information")
        self.refresh()

