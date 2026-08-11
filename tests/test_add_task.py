"""
Regression tests for tasks.add_task().

Install pytest first:
    pip install pytest

Run from the project root with:
    pytest tests/test_add_task.py -v
"""

import storage
import tasks
from storage import Task


def test_add_task_appends_task_with_eta(storage_csv, monkeypatch):
    task_list: list[Task] = []
    responses = iter(["Wash the car", "2026-08-20"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.add_task(task_list)
    assert task_list == [{"task": "Wash the car", "eta": "2026-08-20"}]


def test_add_task_persists_to_csv(storage_csv, monkeypatch):
    task_list: list[Task] = []
    responses = iter(["Read a book", "2026-09-01"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.add_task(task_list)
    assert storage.load_tasks() == [{"task": "Read a book", "eta": "2026-09-01"}]


def test_add_task_rejects_empty_task_then_accepts_valid(storage_csv, monkeypatch):
    task_list: list[Task] = []
    responses = iter(["   ", "Valid task", "2026-08-20"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.add_task(task_list)
    assert task_list == [{"task": "Valid task", "eta": "2026-08-20"}]


def test_add_task_rejects_invalid_eta_then_accepts_valid(storage_csv, monkeypatch):
    task_list: list[Task] = []
    responses = iter(["Valid task", "not-a-date", "2026-08-20"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.add_task(task_list)
    assert task_list == [{"task": "Valid task", "eta": "2026-08-20"}]
