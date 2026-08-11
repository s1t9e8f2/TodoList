"""
Regression tests for tasks.display_tasks().

Install pytest first:
    pip install pytest

Run from the project root with:
    pytest tests/test_display_tasks.py -v
"""

import tasks
from storage import Task


def test_display_tasks_empty_list(capsys):
    tasks.display_tasks([])
    captured = capsys.readouterr()
    assert "No tasks in the list." in captured.out


def test_display_tasks_shows_header_and_rows(capsys):
    task_list: list[Task] = [
        {"task": "First", "eta": "2026-08-17"},
        {"task": "Second", "eta": "2026-08-20"},
    ]
    tasks.display_tasks(task_list)
    captured = capsys.readouterr()
    assert "Number" in captured.out
    assert "Task" in captured.out
    assert "ETA" in captured.out
    assert "First" in captured.out
    assert "2026-08-17" in captured.out
    assert "Second" in captured.out
    assert "2026-08-20" in captured.out
