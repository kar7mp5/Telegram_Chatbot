from os.path import dirname
from sys import path

path.insert(0, dirname(__file__))

from .chat_history import init_user_db, init_chat_db, save_message, load_messages