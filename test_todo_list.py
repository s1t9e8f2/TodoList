"""
Regression tests for todo_list.py 

"""

import io
import sys
import pytest
import todo_list


@pytest.fixture
def todo_list_csv(tmp_path, monkeypatch):
  """Point CSV_FILE at a temporary file for the duration of a test."""
  csv_path = tmp_path / 'MyTasks.csv'
  monkeypatch.setattr(todo_list, 'CSV_FILE', str(csv_path))
  return str(csv_path)


# --- load_tasks / save_tasks ---------------------------------------------

def test_load_tasks_creates_empty_file_if_missing(todo_list_csv):
  assert not __import__('os').path.exists(todo_list_csv)
  tasks = todo_list.load_tasks()
  assert tasks == []
  assert __import__('os').path.exists(todo_list_csv)


def test_save_and_load_roundtrip_cyrillic_and_latin(todo_list_csv):
  original = ['Купи мляко', 'Buy bread', 'Смесен Task 123']
  todo_list.save_tasks(original)
  assert todo_list.load_tasks() == original


def test_load_tasks_returns_existing_tasks(todo_list_csv):
  todo_list.save_tasks(['Test task'])
  assert todo_list.load_tasks() == ['Test task']


# --- add_task --------------------------------------------------------

def test_add_task_appends_valid_task(todo_list_csv, monkeypatch):
  tasks = []
  monkeypatch.setattr('builtins.input', lambda _: 'Wash the car')
  todo_list.add_task(tasks)
  assert tasks == ['Wash the car']


def test_add_task_persists_to_csv(todo_list_csv, monkeypatch):
  tasks = []
  monkeypatch.setattr('builtins.input', lambda _: 'Read a book')
  todo_list.add_task(tasks)
  assert todo_list.load_tasks() == ['Read a book']


def test_add_task_rejects_empty_then_accepts_valid(todo_list_csv, monkeypatch):
  tasks = []
  responses = iter(['   ', 'Valid task'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  todo_list.add_task(tasks)
  assert tasks == ['Valid task']


# --- remove_task -----------------------------------------------------

def test_remove_task_removes_correct_item(todo_list_csv, monkeypatch):
  tasks = ['Task A', 'Task B', 'Task C']
  monkeypatch.setattr('builtins.input', lambda _: '2')
  todo_list.remove_task(tasks)
  assert tasks == ['Task A', 'Task C']


def test_remove_task_persists_to_csv(todo_list_csv, monkeypatch):
  tasks = ['Task A', 'Task B']
  monkeypatch.setattr('builtins.input', lambda _: '1')
  todo_list.remove_task(tasks)
  assert todo_list.load_tasks() == ['Task B']


def test_remove_task_rejects_out_of_range_then_accepts_valid(todo_list_csv, monkeypatch):
  tasks = ['Task A', 'Task B']
  responses = iter(['5', '1'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  todo_list.remove_task(tasks)
  assert tasks == ['Task B']


def test_remove_task_rejects_non_numeric_then_accepts_valid(todo_list_csv, monkeypatch):
  tasks = ['Task A']
  responses = iter(['abc', '1'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  todo_list.remove_task(tasks)
  assert tasks == []


# --- display_tasks ---------------------------------------------------

def test_display_tasks_empty_list(capsys):
  todo_list.display_tasks([])
  captured = capsys.readouterr()
  assert 'No tasks in the list.' in captured.out


def test_display_tasks_numbers_items_starting_at_one(capsys):
  todo_list.display_tasks(['First', 'Second'])
  captured = capsys.readouterr()
  assert '1. First' in captured.out
  assert '2. Second' in captured.out


# --- get_choice --------------------------------------------------------

def test_get_choice_returns_valid_choice(monkeypatch):
  monkeypatch.setattr('builtins.input', lambda _: '2')
  assert todo_list.get_choice() == '2'


def test_get_choice_rejects_invalid_then_accepts_valid(monkeypatch):
  responses = iter(['9', '4'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  assert todo_list.get_choice() == '4'
