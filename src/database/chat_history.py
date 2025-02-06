import sqlite3

def init_user_db():
    """
    Initializes a SQLite database to store user information.

    The database 'users.db' contains a table with user_id and username.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT
        )
    ''')
    conn.commit()
    conn.close()

def _add_user(user_id, username):
    """
    Adds a user to the user database if they are not already present.

    Args:
        user_id (int): The Telegram user's unique ID.
        username (str): The Telegram user's username.
    """
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
    conn.commit()
    conn.close()

def init_chat_db():
    """
    Initializes a SQLite database to store chat messages.

    The database 'chat_history.db' contains messages linked to user_id.
    """
    conn = sqlite3.connect('chat_history.db')
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

def save_message(user_id, username, message):
    """
    Saves a user's message into the chat database.

    Args:
        user_id (int): The Telegram user's unique ID.
        username (str): The Telegram user's username.
        message (str): The message text to be saved.
    """
    _add_user(user_id, username)
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (user_id, username, message)
        VALUES (?, ?, ?)
    ''', (user_id, username, message))
    conn.commit()
    conn.close()

def load_messages(user_id):
    """
    Loads all messages for a specific user from the chat database.

    Args:
        user_id (int): The Telegram user's unique ID.

    Returns:
        list: A list of tuples containing message records.
    """
    conn = sqlite3.connect('chat_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, message, timestamp FROM messages WHERE user_id = ?', (user_id,))
    messages = cursor.fetchall()
    conn.close()
    return messages