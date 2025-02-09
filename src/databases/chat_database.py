import sqlite3
import os
import logging
from tools import setup_logger

# Initialize logger configuration
setup_logger()
logger = logging.getLogger(__name__)

# Define database paths
_BASE_PATH = os.path.join(os.getcwd(), "user_database")
_CHAT_HISTORY_PATH = os.path.join(_BASE_PATH, "chat_history")

# Ensure required directories exist
if not os.path.isdir(_BASE_PATH):
    os.mkdir(_BASE_PATH)
    logger.info("User database directory has been created.")

if not os.path.isdir(_CHAT_HISTORY_PATH):
    os.mkdir(_CHAT_HISTORY_PATH)
    logger.info("Chat history directory has been created.")

# Define user database file path
_USER_DATABASE_PATH = os.path.join(_BASE_PATH, "users.db")


def _get_chat_db_path(user_id: int, username: str) -> str:
    """
    Generates the database file path for a user's chat history.

    Args:
        user_id (int): Unique identifier of the user.
        username (str): Telegram username of the user.

    Returns:
        str: The file path of the user's chat database.
    """
    sanitized_username = "".join(c if c.isalnum() or c in ("_", "-") else "" for c in username)
    return os.path.join(_CHAT_HISTORY_PATH, f"{sanitized_username}_{user_id}.db")


def init_user_db():
    """
    Initializes the SQLite database to store user information.

    This function creates a 'users' table if it does not already exist.
    """
    conn = sqlite3.connect(_USER_DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT
        )
    ''')
    conn.commit()
    conn.close()


def _add_user(user_id: int, username: str):
    """
    Adds a user to the user database if they are not already registered.

    Args:
        user_id (int): Unique identifier of the user.
        username (str): Telegram username of the user.
    """
    conn = sqlite3.connect(_USER_DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()
    conn.close()


def _init_chat_db(user_id: int, username: str):
    """
    Initializes the SQLite database to store chat messages for a specific user.

    This function creates a 'messages' table if it does not already exist.

    Args:
        user_id (int): Unique identifier of the user.
        username (str): Telegram username of the user.
    """
    db_path = _get_chat_db_path(user_id, username)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            sender TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def save_message(user_id: int, username: str, sender: str, message: str):
    """
    Saves a chat message to the database.

    Args:
        user_id (int): Unique identifier of the user.
        username (str): Telegram username of the user.
        sender (str): Either 'user' or 'bot', indicating who sent the message.
        message (str): The text content of the message.
    """
    _add_user(user_id, username)
    _init_chat_db(user_id, username)
    db_path = _get_chat_db_path(user_id, username)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (user_id, username, sender, message)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, sender, message))
    conn.commit()
    conn.close()


def load_messages(user_id: int, username: str) -> list:
    """
    Retrieves all chat messages for a specific user.

    Args:
        user_id (int): Unique identifier of the user.
        username (str): Telegram username of the user.

    Returns:
        list: A list of tuples containing message records (username, sender, message, timestamp).
    """
    db_path = _get_chat_db_path(user_id, username)
    if not os.path.exists(db_path):
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT username, sender, message, timestamp FROM messages WHERE user_id = ?', (user_id,))
    messages = cursor.fetchall()
    conn.close()
    return messages


def delete_messages(user_id: int, username: str):
    """
    Deletes all chat messages associated with a specific user.

    Args:
        user_id (int): Unique identifier of the user.
        username (str): Telegram username of the user.
    """
    db_path = _get_chat_db_path(user_id, username)
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM messages WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()