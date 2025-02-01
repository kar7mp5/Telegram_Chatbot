from os.path import dirname
from sys import path

path.insert(0, dirname(__file__))

from .Text2Markdown import text2markdown