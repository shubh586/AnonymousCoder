import os
import tempfile

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.agent_project.infrastructure.databases.sql_database import \
    DataBaseManager


@pytest.fixture
def db_manager():
    # Create a temporary database path
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    tmp_file.close()
    db = DataBaseManager(db_path=tmp_file.name)
    yield db
    db.close()
    os.unlink(tmp_file.name)


def test_thread_creation_and_listing(db_manager):
    db_manager.create_thread("t1", "Test Thread")
    threads = db_manager.list_threads()
    assert any("t1 Test Thread" in t for t in threads)


def test_add_and_get_messages(db_manager):
    db_manager.create_thread("t1", "Test Thread")
    db_manager.add_human_message("t1", "m1", "Hello")
    db_manager.add_ai_message("t1", "m2", "Hi there!")

    messages = db_manager.get_messages("t1")
    assert isinstance(messages[0], HumanMessage)
    assert messages[0].content == "Hello"
    assert isinstance(messages[1], AIMessage)
    assert messages[1].content == "Hi there!"


def test_add_message_obj(db_manager):
    db_manager.create_thread("t1", "Test Thread")
    db_manager.add_message_obj("t1", "m1", HumanMessage(content="Hi"))
    db_manager.add_message_obj("t1", "m2", AIMessage(content="Hello"))

    messages = db_manager.get_messages("t1")
    assert messages[0].content == "Hi"
    assert messages[1].content == "Hello"


def test_raw_messages(db_manager):
    db_manager.create_thread("t1", "Test Thread")
    db_manager.add_human_message("t1", "m1", "Hello raw")
    rows = db_manager.get_raw_messages("t1")
    assert rows[0]["content"] == "Hello raw"
    assert rows[0]["role"] == "human"


def test_delete_thread(db_manager):
    db_manager.create_thread("t1", "ToDelete")
    db_manager.add_human_message("t1", "m1", "Hi")
    db_manager.delete_thread("t1")
    threads = db_manager.list_threads()
    assert not any("t1 ToDelete" in t for t in threads)
    # Messages should also be deleted due to CASCADE
    rows = db_manager.get_raw_messages("t1")
    assert rows == []
