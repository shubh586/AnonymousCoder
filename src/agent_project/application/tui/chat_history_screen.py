import uuid

from textual.app import ComposeResult
from textual.containers import Container, HorizontalGroup
from textual.screen import Screen
from textual.widgets import Button, Label, ListItem, ListView, Static, TextArea


class ChatHistoryScreen(Screen):
    """Screen for managing chat history"""
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("d", "delete_thread", "Delete Thread"),
        ("r", "rename_thread", "Rename Thread"),
    ]
    
    def __init__(self):
        super().__init__()
        self.chat_threads = [
            {
                "id": str(uuid.uuid4()),
                "title": "Python Debugging Session",
                "created": "2024-01-16 09:00",
                "message_count": 15,
                "last_message": "Thanks for helping with the bug fix!"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Database Schema Design",
                "created": "2024-01-15 14:30",
                "message_count": 8,
                "last_message": "The normalized schema looks good now."
            },
            {
                "id": str(uuid.uuid4()),
                "title": "API Development Questions",
                "created": "2024-01-14 11:15",
                "message_count": 23,
                "last_message": "Perfect! The REST endpoints are working."
            }
        ]
    
    def compose(self) -> ComposeResult:
        # Create list view for chat threads
        list_view = ListView(id="chat_threads_list")
        
        for thread in self.chat_threads:
            list_view.append(
                ListItem(
                    Label(f"[bold]{thread['title']}[/bold]"),
                    Label(f"Created: {thread['created']} | Messages: {thread['message_count']}"),
                    Label(f"Last: {thread['last_message'][:50]}..."),
                )
            )
        
        yield Container(
            Static("[bold green]Chat History[/bold green]", classes="title"),
            HorizontalGroup(
                Button("Load Thread", variant="primary", id="load_thread_btn"),
                Button("Rename Thread", variant="default", id="rename_thread_btn"),
                Button("Delete Thread", variant="error", id="delete_thread_btn"),
                Button("Export Thread", variant="default", id="export_thread_btn"),
                classes="button-group"
            ),
            list_view,
            TextArea(
                text="Select a chat thread to view details...",
                id="thread_preview",
                read_only=True
            ),
            HorizontalGroup(
                Button("Back", variant="default", id="back_button"),
                classes="bottom-buttons"
            ),
            id="history_container"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_button":
            self.app.pop_screen()
        elif event.button.id == "load_thread_btn":
            self.load_selected_thread()
        elif event.button.id == "delete_thread_btn":
            self.delete_selected_thread()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Show thread preview when selected"""
        if event.item and hasattr(event.item, 'index'):
            thread = self.chat_threads[event.item.index]
            preview_area = self.query_one("#thread_preview", TextArea)
            preview_area.text = f"Thread: {thread['title']}\nCreated: {thread['created']}\nMessages: {thread['message_count']}\n\nLast Message: {thread['last_message']}"
    
    def load_selected_thread(self) -> None:
        self.notify("Thread loaded successfully!", severity="information")
        self.app.pop_screen()
    
    def delete_selected_thread(self) -> None:
        list_view = self.query_one("#chat_threads_list", ListView)
        if list_view.index is not None:
            del self.chat_threads[list_view.index]
            list_view.clear()
            for thread in self.chat_threads:
                list_view.append(
                    ListItem(
                        Label(f"[bold]{thread['title']}[/bold]"),
                        Label(f"Created: {thread['created']} | Messages: {thread['message_count']}"),
                        Label(f"Last: {thread['last_message'][:50]}..."),
                    )
                )
            self.notify("Thread deleted successfully!", severity="information")
