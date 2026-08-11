"""
Regression tests for tasks.list_urgent_tasks().

Install pytest first:
    pip install pytest

Run from the project root with:
    pytest tests/test_list_urgent_tasks.py -v
"""

from datetime import date, timedelta

from colorama import Fore, Style

import tasks
from storage import Task


def test_list_urgent_tasks_returns_immediately_when_list_is_empty(monkeypatch):
    def input_should_not_be_called(_):
        raise AssertionError("input() should not be called when the task list is empty")

    monkeypatch.setattr("builtins.input", input_should_not_be_called)
    tasks.list_urgent_tasks([])  # must not hang or raise


def test_list_urgent_tasks_shows_tasks_within_window_sorted_by_eta(monkeypatch, capsys):
    today = date.today()
    task_list: list[Task] = [
        {"task": "Later task", "eta": (today + timedelta(days=5)).strftime("%Y-%m-%d")},
        {
            "task": "Sooner task",
            "eta": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
        },
    ]
    monkeypatch.setattr("builtins.input", lambda _: "7")
    tasks.list_urgent_tasks(task_list)

    output = capsys.readouterr().out
    sooner_index = output.index("Sooner task")
    later_index = output.index("Later task")
    assert sooner_index < later_index, "Sooner task should be listed first"


def test_list_urgent_tasks_excludes_tasks_outside_window(monkeypatch, capsys):
    today = date.today()
    task_list: list[Task] = [
        {
            "task": "Within window",
            "eta": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
        },
        {
            "task": "Outside window",
            "eta": (today + timedelta(days=30)).strftime("%Y-%m-%d"),
        },
    ]
    monkeypatch.setattr("builtins.input", lambda _: "7")
    tasks.list_urgent_tasks(task_list)

    output = capsys.readouterr().out
    assert "Within window" in output
    assert "Outside window" not in output


def test_list_urgent_tasks_includes_and_warns_about_overdue_tasks(monkeypatch, capsys):
    today = date.today()
    task_list: list[Task] = [
        {
            "task": "Overdue task",
            "eta": (today - timedelta(days=3)).strftime("%Y-%m-%d"),
        },
        {
            "task": "Upcoming task",
            "eta": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
        },
    ]
    monkeypatch.setattr("builtins.input", lambda _: "7")
    tasks.list_urgent_tasks(task_list)

    output = capsys.readouterr().out
    assert "WARNING" in output
    assert "OVERDUE" in output
    assert "Overdue task" in output
    # The overdue task must also be listed first (soonest/most urgent).
    assert output.index("Overdue task") < output.index("Upcoming task")


def test_list_urgent_tasks_colors_overdue_status_red_and_bold(monkeypatch, capsys):
    """The OVERDUE label (and the warning banner) should be colored red
    and bold in the terminal - and only for overdue rows, not the whole
    table."""
    today = date.today()
    task_list: list[Task] = [
        {
            "task": "Overdue task",
            "eta": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
        },
        {
            "task": "Upcoming task",
            "eta": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
        },
    ]
    monkeypatch.setattr("builtins.input", lambda _: "7")
    tasks.list_urgent_tasks(task_list)

    output = capsys.readouterr().out
    assert Fore.RED in output
    assert Style.BRIGHT in output
    assert Style.RESET_ALL in output

    upcoming_line = next(
        line for line in output.splitlines() if "Upcoming task" in line
    )
    assert Fore.RED not in upcoming_line


def test_list_urgent_tasks_shows_message_when_none_match(monkeypatch, capsys):
    today = date.today()
    task_list: list[Task] = [
        {"task": "Far away", "eta": (today + timedelta(days=30)).strftime("%Y-%m-%d")},
    ]
    monkeypatch.setattr("builtins.input", lambda _: "5")
    tasks.list_urgent_tasks(task_list)

    output = capsys.readouterr().out
    assert "No tasks due within the next 5 day(s)." in output


def test_list_urgent_tasks_rejects_invalid_days_then_accepts_valid(monkeypatch, capsys):
    today = date.today()
    task_list: list[Task] = [{"task": "Due today", "eta": today.strftime("%Y-%m-%d")}]
    responses = iter(["-1", "abc", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    tasks.list_urgent_tasks(task_list)

    output = capsys.readouterr().out
    assert "Please enter a number of days that is 0 or greater." in output
    assert "Please enter a whole number." in output
    assert "Due today" in output
