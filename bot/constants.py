"""
constants.py

Stores constants like paths to various locations, integers/strings or simple generated classes.
"""

import logging
import os

from collections import namedtuple

# Path Constants
BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, '..')))
STATIC_DIR = os.path.join(BASE_DIR, 'bot', 'static')
TOKEN = os.path.join(BASE_DIR, 'token.dat')
DATABASE = os.path.join(BASE_DIR, 'database.db')

# Other constants
LOGGING_LEVEL = logging.DEBUG

# NamedTuple Classes
PlayOptions = namedtuple('PlayOptions', ['hit', 'stand', 'double', 'split'])
