from os.path import dirname
from sys import path

path.insert(0, dirname(__file__))

from .chat_database import init_user_db, save_message, load_messages, delete_messages