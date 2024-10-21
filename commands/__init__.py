# __init__.py
from os.path import dirname
from sys import path


path.insert(0, dirname(__file__))


from .start import start
from .help import help
from .weather import weather
from .gpt_response import gpt_response, handle_callback_query
from .unknown import unknown