"""
Regression tests for tasks.py.

tasks.py calls storage.save_tasks() internally, so these tests point
storage.CSV_FILE at a temporary file (same technique as test_storage.py)
to avoid touching the real MyTasks.csv.

Install pytest first:
    pip install pytest

Run from the project root with:
    pytest tests/test_tasks.py -v
"""

import pytest

import storage
import tasks
from storage import Task


@pytest.fixture
def storage_csv(tmp_path, monkeypatch):
    """Point CSV_FILE at a temporary file for the duration of a test."""
    csv_path = tmp_path / "MyTasks.csv"
    monkeypatch.setattr(storage, "CSV_FILE", str(csv_path))
    return str(csv_path)


# --- add_task ------------------------------------------------------------


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


# --- remove_task ----------------------------------------------------


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


# --- display_tasks -----------------------------------------------------


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
