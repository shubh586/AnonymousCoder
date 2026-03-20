import sqlite3
from datetime import datetime
from typing import List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from pydantic import BaseModel, Field


class DataBaseManager(BaseModel):
    """SQLite conversation store for threads and messages."""

    db_path: str = Field(default="user_space/history.db")
    
    # allows the types that arent validated by Pydantic
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, db_path: str = "user_space/history.db"):
        # for validation purposes in  pydantic
        super().__init__(db_path=db_path)
        # Use object.__setattr__ to bypass Pydantic's validation for non-standard types
        object.__setattr__(self, 'conn', sqlite3.connect(self.db_path, check_same_thread=False))
        self.conn.execute("PRAGMA foreign_keys = ON;")
        # for making the outputs like dicts not tuples ( helps in readiablity tuple row[0] , dict is row['thread_id'])
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS threads (
                thread_id TEXT PRIMARY KEY,
                title TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        # Messages table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                thread_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('human','ai')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(thread_id) REFERENCES threads(thread_id) ON DELETE CASCADE
            );
            """
        )
        self.conn.commit()

    def create_thread(self, thread_id: str, title: str) -> None:
        """Create a thread if it doesn't exist."""
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT OR IGNORE INTO threads (thread_id, title, created_at)
            VALUES (?, ?, ?)
            """,
            (thread_id, title, datetime.utcnow().isoformat()),
        )
        self.conn.commit()
        
    def alter_thread_title(self, thread_id: str, title: str) -> None:
        curr = self.conn.cursor()
        curr.execute(
            """
            UPDATE threads SET title = ? WHERE thread_id = ?
            """,
            (title, thread_id)
        )
        self.conn.commit()

    def delete_thread(self, thread_id: str) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM threads WHERE thread_id = ?", (thread_id,))
        self.conn.commit()

    def list_threads(self) -> List[str]:
        cur = self.conn.cursor()
        rows = cur.execute(
            "SELECT thread_id, title FROM threads ORDER BY created_at DESC"
        ).fetchall()
        return [f"{row['thread_id']} {row['title']}" for row in rows]

    def add_human_message(self, thread_id: str, message_id: str, content: str) -> None:
        self._add_message(thread_id, message_id, role="human", content=content)

    def add_ai_message(self, thread_id: str, message_id: str, content: str) -> None:
        self._add_message(thread_id, message_id, role="ai", content=content)

    def add_message_obj(self, thread_id: str, message_id: str, message: BaseMessage) -> None:
        if isinstance(message, HumanMessage):
            self.add_human_message(thread_id, message_id, str(message.content))
        elif isinstance(message, AIMessage):
            self.add_ai_message(thread_id, message_id, str(message.content))
        else:
            raise ValueError("Unsupported message type. Use HumanMessage or AIMessage.")

    def _add_message(self, thread_id: str, message_id: str, role: str, content: str) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO messages (message_id, thread_id, role, content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (message_id, thread_id, role, content, datetime.now().isoformat()),
        )
        self.conn.commit()

    def get_messages(self, thread_id: str) -> List[BaseMessage]:
        """Return messages as LangChain message objects (HumanMessage/AIMessage)."""
        cur = self.conn.cursor()
        rows = cur.execute(
            """
            SELECT role, content
            FROM messages
            WHERE thread_id = ?
            ORDER BY created_at ASC
            """,
            (thread_id,),
        ).fetchall()
        messages: List[BaseMessage] = []
        for row in rows:
            if row["role"] == "human":
                messages.append(HumanMessage(content=row["content"]))
            else:
                messages.append(AIMessage(content=row["content"]))
        return messages

    def get_raw_messages(self, thread_id: str) -> List[sqlite3.Row]:
        """Return raw message rows for custom needs."""
        cur = self.conn.cursor()
        return cur.execute(
            "SELECT * FROM messages WHERE thread_id = ? ORDER BY created_at ASC",
            (thread_id,),
        ).fetchall()

    def close(self) -> None:
        self.conn.close()

def get_database_manager(db_path: str = "user_space/history.db"):
    return DataBaseManager(db_path=db_path)