import sqlite3
import os

import logging
from tools import setup_logger

class ChatDatabase:
    """A class representing a simple database.

    This class manages a database with a specified path.
    """

    # Initialize the logger configuration
    setup_logger()
    logger = logging.getLogger(__name__)

    # Check 'user_databse' directory is existed
    _base_path: str = os.path.join(os.getcwd(), "user_database")
    if not os.path.isdir(_base_path):
        os.mkdir("user_database")
        logging.info("user database directory is created.")

    # Set database path
    USER_DATABASE_PATH: str = os.path.join(_base_path, "users.db")
    CHAT_HISTORY_DATABASE_PATH: str = os.path.join(_base_path, "chat_history.db")

    def init_user_db(self):
        """
        Initializes a SQLite database to store user information.

        The database 'users.db' contains a table with user_id and username.
        """
        conn = sqlite3.connect(self.USER_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _add_user(self, user_id: int, username: str):
        """
        Adds a user to the user database if they are not already present.

        Args:
            user_id (int): The Telegram user's unique ID.
            username (str): The Telegram user's username.
        """
        conn = sqlite3.connect(self.USER_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
        conn.commit()
        conn.close()

    def init_chat_db(self):
        """
        Initializes a SQLite database to store chat messages.

        The database 'chat_history.db' contains messages linked to user_id.
        """
        conn = sqlite3.connect(self.CHAT_HISTORY_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        ''')
        conn.commit()
        conn.close()

    def save_message(self, user_id: int, username: str, message: str):
        """
        Saves a user's message into the chat database.

        Args:
            user_id (int): The Telegram user's unique ID.
            username (str): The Telegram user's username.
            message (str): The message text to be saved.
        """
        self._add_user(user_id, username)
        conn = sqlite3.connect(self.CHAT_HISTORY_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (user_id, username, message)
            VALUES (?, ?, ?)
        ''', (user_id, username, message))
        conn.commit()
        conn.close()

    def load_messages(self, user_id: int) -> list:
        """
        Loads all messages for a specific user from the chat database.

        Args:
            user_id (int): The Telegram user's unique ID.

        Returns:
            list: A list of tuples containing message records.
        """
        conn = sqlite3.connect(self.CHAT_HISTORY_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT username, message, timestamp FROM messages WHERE user_id = ?', (user_id,))
        messages = cursor.fetchall()
        conn.close()
        return messages
    
    def delete_messages(self, user_id: int):
        """
        Deletes all messages for a specific user from the chat database.

        Args:
            user_id (int): The Telegram user's unique ID.
        """
        conn = sqlite3.connect(self.CHAT_HISTORY_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM messages WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()