"""
Regression tests for tasks.remove_task().

Install pytest first:
    pip install pytest

Run from the project root with:
    pytest tests/test_remove_task.py -v
"""

import storage
import tasks
from storage import Task


def test_remove_task_removes_correct_item_by_number(storage_csv, monkeypatch):
    task_list: list[Task] = [
        {"task": "Task A", "eta": "2026-08-01"},
        {"task": "Task B", "eta": "2026-08-02"},
        {"task": "Task C", "eta": "2026-08-03"},
    ]
    monkeypatch.setattr("builtins.input", lambda _: "2")
    tasks.remove_task(task_list)
    assert task_list == [
        {"task": "Task A", "eta": "2026-08-01"},
        {"task": "Task C", "eta": "2026-08-03"},
    ]


def test_remove_task_persists_to_csv(storage_csv, monkeypatch):
    task_list: list[Task] = [
        {"task": "Task A", "eta": "2026-08-01"},
        {"task": "Task B", "eta": "2026-08-02"},
    ]
    monkeypatch.setattr("builtins.input", lambda _: "1")
    tasks.remove_task(task_list)
    assert storage.load_tasks() == [{"task": "Task B", "eta": "2026-08-02"}]


def test_remove_task_rejects_out_of_range_then_accepts_valid(storage_csv, monkeypatch):
    task_list: list[Task] = [
        {"task": "Task A", "eta": "2026-08-01"},
        {"task": "Task B", "eta": "2026-08-02"},
    ]
    responses = iter(["5", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.remove_task(task_list)
    assert task_list == [{"task": "Task B", "eta": "2026-08-02"}]


def test_remove_task_rejects_non_numeric_then_accepts_valid(storage_csv, monkeypatch):
    task_list: list[Task] = [{"task": "Task A", "eta": "2026-08-01"}]
    responses = iter(["abc", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.remove_task(task_list)
    assert task_list == []


def test_remove_task_returns_immediately_when_list_is_empty(storage_csv, monkeypatch):
    """Regression test: remove_task() used to loop forever asking for a
    task number when the list was empty, since no number could ever be
    in range. It should now return right away without calling input()."""
    task_list: list[Task] = []

    def input_should_not_be_called(_):
        raise AssertionError("input() should not be called when the task list is empty")

    monkeypatch.setattr("builtins.input", input_should_not_be_called)
    tasks.remove_task(task_list)  # must not hang or raise
    assert task_list == []
