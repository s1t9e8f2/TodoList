"""
Makes sure pytest can import modules from the project root (one level
up from tests/) when running `pytest` or `pytest tests/`, regardless
of the current working directory.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
