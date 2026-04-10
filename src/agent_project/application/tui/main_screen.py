import os
import platform
from datetime import datetime
from threading import Thread
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Footer, Input
from textual import work
from textual.worker import Worker


class IntroHeader(Widget):

    def render(self):
        return """

[bold #bae51a]
 █████  ███    ██  ██████  ███    ██ ██    ██ ███    ███  ██████  ██    ██ ███████ 
██   ██ ████   ██ ██    ██ ████   ██  ██  ██  ████  ████ ██    ██ ██    ██ ██      
███████ ██ ██  ██ ██    ██ ██ ██  ██   ████   ██ ████ ██ ██    ██ ██    ██ ███████ 
██   ██ ██  ██ ██ ██    ██ ██  ██ ██    ██    ██  ██  ██ ██    ██ ██    ██      ██ 
██   ██ ██   ████  ██████  ██   ████    ██    ██      ██  ██████   ██████  ███████
[/bold #bae51a]
    
[bold white]
 ██████  ██████  ██████  ███████ ██████  
██      ██    ██ ██   ██ ██      ██   ██ 
██      ██    ██ ██   ██ █████   ██████  
██      ██    ██ ██   ██ ██      ██   ██ 
 ██████  ██████  ██████  ███████ ██   ██ 
[/bold white]

        [bold #bae51a]Quick Commands:[/bold #bae51a]
        [bold #e3b81c]@[/bold #e3b81c] - Reference files and directories
        [bold #e3b81c]search:[/bold #e3b81c] - Search through memories
        [bold #e3b81c]ter:[/bold #e3b81c] - Execute terminal commands
        [bold #e3b81c]bye[/bold #e3b81c] or [bold #e3b81c]exit[/bold #e3b81c] - Quit application

        [bold #bae51a]Keybindings:[/bold #bae51a]
        [bold #e3b81c]s[/bold #e3b81c] - Settings
        [bold #e3b81c]m[/bold #e3b81c] - Manage Memories  
        [bold #e3b81c]h[/bold #e3b81c] - Chat History
        [bold #e3b81c]Ctrl+C[/bold #e3b81c] - Quit
        """


class ChatMessage(Widget):
    """Widget for displaying chat messages"""

    def __init__(self, role: str, content: str, timestamp: str):
        super().__init__()
        self.role = role
        self.content = content
        self.timestamp = timestamp

    def render(self) -> str:
        role_color = "yellow" if self.role == "user" else "#bae51a"
        return f"[{role_color}]{self.role.upper()}[/{role_color}] [{self.timestamp}]\n{self.content}\n"


class MainScreen(Screen):
    """Main chat interface screen"""

    messages_shown = reactive(False)

    def __init__(self, graph=None, config=None, database=None):
        super().__init__()
        self.chat_messages = []
        self.graph = graph
        self.config = config or {"configurable": {"thread_id": str(uuid4())}}
        self.database = database
        self.first_chat = True
        self.system_prompt = None
        self.thread_id = self.config.get("configurable", {}).get("thread_id", str(uuid4()))

    def compose(self) -> ComposeResult:
        yield VerticalScroll(
            IntroHeader(), 
            Container(id="chat_container"), 
            id="main_scroll"
        )
        with Container(id="input_container"):
            yield Input(
                placeholder="What's on your mind today...", 
                id="user_input"
            )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize system prompt on mount."""
        from src.agent_project.core.prompts.system_prompt import get_system_prompt
        self.system_prompt = get_system_prompt(
            os=platform.system(),
            path=os.getcwd()
        )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input submission"""
        if event.value.strip():
            query = event.value.strip()

            if query.lower() in {"bye", "exit"}:
                self.app.exit()
                return

            # Show user message in chat
            self.add_message("user", query)

            # Clear input
            event.input.value = ""

            # Store in DB if available
            if self.database:
                try:
                    self.database.create_thread(thread_id=self.thread_id, title=query[:50])
                    self.database.add_human_message(
                        thread_id=self.thread_id,
                        message_id=str(uuid4()),
                        content=query
                    )
                except Exception:
                    pass

            # If graph is available, run the agent
            if self.graph:
                self.run_agent(query)
            else:
                self.add_message("assistant", "❌ LLM not available. Please check your configuration.")

    @work(thread=True)
    def run_agent(self, query: str) -> None:
        """Run the LangGraph agent in a background thread."""
        from src.agent_project.utilities.logger import init_logger
        log = init_logger(enable_logging=True, log_file="user_space/logs.log")

        # Show thinking indicator
        self.app.call_from_thread(self.add_message, "assistant", "🤔 Thinking...")

        try:
            # Build the input state
            if self.first_chat:
                self.first_chat = False
                input_state = {
                    "query": query,
                    "messages": [
                        SystemMessage(content=self.system_prompt),
                        HumanMessage(content=query)
                    ],
                    "type": ""
                }
            else:
                input_state = {
                    "query": query,
                    "messages": [HumanMessage(content=query)],
                    "type": ""
                }

            log.info(f"TUI: Invoking graph with query: {query[:80]}")
            output = self.graph.invoke(input_state, self.config)
            log.info("TUI: Graph invocation completed")

            # Extract the AI response
            messages = output.get("messages", [])
            response = "Task completed."
            if messages:
                for msg in reversed(messages):
                    if hasattr(msg, 'type') and msg.type == 'ai':
                        response = msg.content
                        break

            # Remove the thinking message and show real response
            self.app.call_from_thread(self._replace_last_message, response)

            # Store AI response in DB
            if self.database:
                try:
                    self.database.add_ai_message(
                        thread_id=self.thread_id,
                        message_id=str(uuid4()),
                        content=str(response)
                    )
                except Exception:
                    pass

        except Exception as e:
            log.error(f"TUI: Agent error: {e}")
            self.app.call_from_thread(self._replace_last_message, f"❌ Error: {e}")

    def add_message(
        self,
        role: str,
        content: str,
        timestamp: str = None,
    ) -> None:
        """Add a new message to the chat"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        message = ChatMessage(role, content, timestamp=timestamp)
        self.chat_messages.append(message)

        chat_container = self.query_one("#chat_container", Container)
        chat_container.mount(message)

        # If this is the first message, hide the intro and scroll
        if not self.messages_shown:
            self.messages_shown = True
        
        main_scroll = self.query_one("#main_scroll", VerticalScroll)
        main_scroll.scroll_end(animate=True)

    def _replace_last_message(self, content: str) -> None:
        """Replace the last assistant message (e.g. thinking indicator) with actual response."""
        if self.chat_messages:
            last_msg = self.chat_messages[-1]
            last_msg.remove()
            self.chat_messages.pop()
        self.add_message("assistant", content)
