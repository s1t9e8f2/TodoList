"""
Regression tests for tasks.edit_task().

Install pytest first:
    pip install pytest

Run from the project root with:
    pytest tests/test_edit_task.py -v
"""

import storage
import tasks
from storage import Task


def test_edit_task_updates_text_and_keeps_eta_when_eta_unchanged(
    storage_csv, monkeypatch
):
    task_list: list[Task] = [{"task": "Old text", "eta": "2026-08-20"}]
    # task number, new text, "keep current ETA" answer
    responses = iter(["1", "New text", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.edit_task(task_list)
    assert task_list == [{"task": "New text", "eta": "2026-08-20"}]


def test_edit_task_updates_eta_and_keeps_text_when_text_left_blank(
    storage_csv, monkeypatch
):
    task_list: list[Task] = [{"task": "Same text", "eta": "2026-08-20"}]
    # task number, blank text (keep current), "change ETA" = yes, new ETA
    responses = iter(["1", "", "y", "2026-09-01"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.edit_task(task_list)
    assert task_list == [{"task": "Same text", "eta": "2026-09-01"}]


def test_edit_task_can_update_both_text_and_eta(storage_csv, monkeypatch):
    task_list: list[Task] = [{"task": "Old text", "eta": "2026-08-20"}]
    responses = iter(["1", "New text", "y", "2026-09-01"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.edit_task(task_list)
    assert task_list == [{"task": "New text", "eta": "2026-09-01"}]


def test_edit_task_persists_to_csv(storage_csv, monkeypatch):
    task_list: list[Task] = [{"task": "Old text", "eta": "2026-08-20"}]
    responses = iter(["1", "New text", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.edit_task(task_list)
    assert storage.load_tasks() == [{"task": "New text", "eta": "2026-08-20"}]


def test_edit_task_edits_correct_item_by_number(storage_csv, monkeypatch):
    task_list: list[Task] = [
        {"task": "Task A", "eta": "2026-08-01"},
        {"task": "Task B", "eta": "2026-08-02"},
    ]
    responses = iter(["2", "Task B edited", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.edit_task(task_list)
    assert task_list == [
        {"task": "Task A", "eta": "2026-08-01"},
        {"task": "Task B edited", "eta": "2026-08-02"},
    ]


def test_edit_task_rejects_out_of_range_then_accepts_valid(storage_csv, monkeypatch):
    task_list: list[Task] = [{"task": "Task A", "eta": "2026-08-01"}]
    responses = iter(["5", "1", "New text", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.edit_task(task_list)
    assert task_list == [{"task": "New text", "eta": "2026-08-01"}]


def test_edit_task_rejects_non_numeric_then_accepts_valid(storage_csv, monkeypatch):
    task_list: list[Task] = [{"task": "Task A", "eta": "2026-08-01"}]
    responses = iter(["abc", "1", "New text", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.edit_task(task_list)
    assert task_list == [{"task": "New text", "eta": "2026-08-01"}]


def test_edit_task_rejects_invalid_new_eta_then_accepts_valid(storage_csv, monkeypatch):
    task_list: list[Task] = [{"task": "Task A", "eta": "2026-08-01"}]
    responses = iter(["1", "New text", "y", "not-a-date", "2026-09-01"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.edit_task(task_list)
    assert task_list == [{"task": "New text", "eta": "2026-09-01"}]


def test_edit_task_rejects_invalid_yn_response_then_accepts_valid(
    storage_csv, monkeypatch
):
    """Regression test: an unrecognized answer to 'Change ETA? (y/n)'
    (e.g. a typo like 'x') used to be silently treated the same as 'n',
    with no feedback. It must now be rejected and re-prompted, consistent
    with the rest of the app's input validation."""
    task_list: list[Task] = [{"task": "Task A", "eta": "2026-08-01"}]
    responses = iter(["1", "New text", "x", "y", "2026-09-01"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.edit_task(task_list)
    assert task_list == [{"task": "New text", "eta": "2026-09-01"}]


def test_edit_task_returns_immediately_when_list_is_empty(storage_csv, monkeypatch):
    """Same pattern as remove_task's empty-list regression test: edit_task()
    must not call input() at all when there is nothing to edit."""
    task_list: list[Task] = []

    def input_should_not_be_called(_):
        raise AssertionError("input() should not be called when the task list is empty")

    monkeypatch.setattr("builtins.input", input_should_not_be_called)
    tasks.edit_task(task_list)  # must not hang or raise
    assert task_list == []
