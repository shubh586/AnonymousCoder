import uuid

from textual.app import ComposeResult
from textual.containers import Container, HorizontalGroup
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DataTable, Input, Label, Static, TextArea


class MemoryManagementScreen(Screen):
    """Screen for managing memories/knowledge base"""
    
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("n", "new_memory", "New Memory"),
        ("d", "delete_memory", "Delete Memory"),
    ]
    
    def __init__(self):
        super().__init__()
        self.memories = [
            {
                "id": str(uuid.uuid4()),
                "title": "Python Best Practices",
                "content": "Always use type hints, follow PEP 8, use virtual environments...",
                "tags": ["python", "best-practices"],
                "created": "2024-01-15 10:30",
                "updated": "2024-01-15 10:30"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Database Schema Design",
                "content": "Normalize to 3NF, use appropriate indexes, consider performance...",
                "tags": ["database", "design"],
                "created": "2024-01-14 15:20",
                "updated": "2024-01-16 09:15"
            }
        ]
    
    def compose(self) -> ComposeResult:
        # Create data table
        table = DataTable(id="memories_table")
        table.add_columns("Title", "Tags", "Created", "Updated")
        
        for memory in self.memories:
            table.add_row(
                memory["title"],
                ", ".join(memory["tags"]),
                memory["created"],
                memory["updated"]
            )
        
        yield Container(
            Static("[bold green]Memory Management[/bold green]", classes="title"),
            HorizontalGroup(
                Button("New Memory", variant="primary", id="new_memory_btn"),
                Button("Edit Memory", variant="default", id="edit_memory_btn"),
                Button("Delete Memory", variant="error", id="delete_memory_btn"),
                Button("Search Memories", variant="default", id="search_memory_btn"),
                classes="button-group"
            ),
            table,
            TextArea(
                text="Select a memory to view its content...",
                id="memory_content",
                read_only=True
            ),
            HorizontalGroup(
                Button("Back", variant="default", id="back_button"),
                classes="bottom-buttons"
            ),
            id="memory_container"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_button":
            self.app.pop_screen()
        elif event.button.id == "new_memory_btn":
            self.app.push_screen(NewMemoryScreen())
        elif event.button.id == "delete_memory_btn":
            self.delete_selected_memory()
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Show memory content when row is selected"""
        if event.row_index < len(self.memories):
            memory = self.memories[event.row_index]
            content_area = self.query_one("#memory_content", TextArea)
            content_area.text = f"Title: {memory['title']}\nTags: {', '.join(memory['tags'])}\n\nContent:\n{memory['content']}"
    
    def delete_selected_memory(self) -> None:
        table = self.query_one("#memories_table", DataTable)
        if table.cursor_row >= 0:
            del self.memories[table.cursor_row]
            table.remove_row(table.cursor_row)
            self.notify("Memory deleted successfully!", severity="information")


class NewMemoryScreen(ModalScreen):
    """Modal screen for creating new memories"""
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("[bold green]Create New Memory[/bold green]", classes="title"),
            Label("Title:"),
            Input(placeholder="Enter memory title...", id="memory_title"),
            Label("Tags (comma-separated):"),
            Input(placeholder="python, tutorial, basics...", id="memory_tags"),
            Label("Content:"),
            TextArea(placeholder="Enter memory content...", id="memory_content_input"),
            HorizontalGroup(
                Button("Save", variant="primary", id="save_memory"),
                Button("Cancel", variant="default", id="cancel_memory"),
            ),
            classes="modal-container"
        )
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save_memory":
            self.save_memory()
        elif event.button.id == "cancel_memory":
            self.app.pop_screen()
    
    def save_memory(self) -> None:
        title = self.query_one("#memory_title", Input).value
        tags = [tag.strip() for tag in self.query_one("#memory_tags", Input).value.split(",")]
        content = self.query_one("#memory_content_input", TextArea).text
        
        if title and content:
            # In a real app, this would be saved to the parent screen
            self.app.pop_screen()
            self.app.notify("Memory saved successfully!", severity="information")
        else:
            self.notify("Please fill in title and content!", severity="error")
