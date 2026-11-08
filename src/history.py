"""
history.py

Manages persistent chat history using SQLite.

Project : AgriAssist
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from logger import get_logger

logger = get_logger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent / "history" / "chat_history.db"

DB_PATH.parent.mkdir(exist_ok=True)


class ChatHistoryManager:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)

        self.cursor = self.conn.cursor()

        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT,

            created_at TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            conversation_id INTEGER,

            role TEXT,

            content TEXT,

            timestamp TEXT,

            FOREIGN KEY(conversation_id)
            REFERENCES conversations(id)
        )
        """)

        self.conn.commit()

    # ----------------------------------

    def create_conversation(self, title="New Conversation"):

        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute(
            """
            INSERT INTO conversations(title, created_at)
            VALUES(?,?)
            """,
            (title, created)
        )

        self.conn.commit()

        return self.cursor.lastrowid

    # ----------------------------------
    # ----------------------------------

    def update_conversation_title(self, conversation_id, title):

        self.cursor.execute(
            """
            UPDATE conversations

            SET title=?

            WHERE id=?
            """,
            (
                title,
                conversation_id
            )
        )

        self.conn.commit()

    def add_message(self, conversation_id, role, content):

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute(
            """
            INSERT INTO messages
            (conversation_id, role, content, timestamp)
            VALUES(?,?,?,?)
            """,
            (
                conversation_id,
                role,
                content,
                ts
            )
        )

        self.conn.commit()

    # ----------------------------------

    def get_messages(self, conversation_id):

        self.cursor.execute(
            """
            SELECT role, content
            FROM messages

            WHERE conversation_id=?

            ORDER BY id
            """,
            (conversation_id,)
        )

        return self.cursor.fetchall()

    # ----------------------------------

    def get_conversations(self):

        self.cursor.execute("""
        SELECT id,title

        FROM conversations

        ORDER BY id DESC
        """)

        return self.cursor.fetchall()

    # ----------------------------------

    def delete_conversation(self, conversation_id):

        self.cursor.execute(
            """
            DELETE FROM messages

            WHERE conversation_id=?
            """,
            (conversation_id,)
        )

        self.cursor.execute(
            """
            DELETE FROM conversations

            WHERE id=?
            """,
            (conversation_id,)
        )

        self.conn.commit()