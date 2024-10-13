# __init__.py
from os.path import dirname
from sys import path

path.insert(0, dirname(__file__))

from .start import start
from .unknown import unknown
from .inline_query import advice, inline_query