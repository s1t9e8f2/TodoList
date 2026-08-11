"""
Makes sure pytest can import modules from the project root (one level
up from tests/) when running `pytest` or `pytest tests/`, regardless
of the current working directory. Also provides shared fixtures used
across multiple test files.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import storage


@pytest.fixture
def storage_csv(tmp_path, monkeypatch):
    """Point CSV_FILE at a temporary file for the duration of a test, so
    tests never read/write the real MyTasks.csv."""
    csv_path = tmp_path / "MyTasks.csv"
    monkeypatch.setattr(storage, "CSV_FILE", str(csv_path))
    return str(csv_path)
