"""
Regression tests for todo_list.py 

Each test gets a fresh temporary CSV file via the `todo_list_csv` fixture.

"""

import os
import pytest
from datetime import date as real_date
import todo_list


@pytest.fixture
def todo_list_csv(tmp_path, monkeypatch):
  """Point CSV_FILE at a temporary file for the duration of a test."""
  csv_path = tmp_path / 'MyTasks.csv'
  monkeypatch.setattr(todo_list, 'CSV_FILE', str(csv_path))
  return str(csv_path)


# --- load_tasks / save_tasks: basics ----------------------------------

def test_load_tasks_creates_empty_file_with_header_if_missing(todo_list_csv):
  assert not os.path.exists(todo_list_csv)
  tasks = todo_list.load_tasks()
  assert tasks == []

  with open(todo_list_csv, encoding='utf-8') as f:
    first_line = f.readline().strip()
  assert first_line == 'Number,Task,ETA'


def test_save_tasks_writes_header_and_rows(todo_list_csv):
  """Tests save_tasks() in isolation by reading the raw bytes on disk,
  instead of trusting load_tasks() to read them back correctly."""
  todo_list.save_tasks([
      {'task': 'Купи мляко', 'eta': '2026-08-17'},
      {'task': 'Buy bread', 'eta': '2026-08-20'},
  ])

  with open(todo_list_csv, mode='rb') as f:
    raw_bytes = f.read()

  expected = (
      'Number,Task,ETA\r\n'
      '1,Купи мляко,2026-08-17\r\n'
      '2,Buy bread,2026-08-20\r\n'
  ).encode('utf-8')
  assert raw_bytes == expected


def test_load_tasks_reads_existing_current_format_rows(todo_list_csv):
  """Tests load_tasks() in isolation by writing the file content by
  hand, instead of trusting save_tasks() to have written it."""
  with open(todo_list_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Number,Task,ETA\r\n')
    f.write('1,Купи мляко,2026-08-17\r\n')
    f.write('2,Buy bread,2026-08-20\r\n')

  tasks = todo_list.load_tasks()
  assert tasks == [
      {'task': 'Купи мляко', 'eta': '2026-08-17'},
      {'task': 'Buy bread', 'eta': '2026-08-20'},
  ]


def test_save_and_load_roundtrip(todo_list_csv):
  original = [
      {'task': 'Купи мляко', 'eta': '2026-08-17'},
      {'task': 'Buy bread', 'eta': '2026-08-20'},
  ]
  todo_list.save_tasks(original)
  assert todo_list.load_tasks() == original


def test_save_tasks_creates_missing_parent_directory(tmp_path, monkeypatch):
  """Regression test: save_tasks() used to crash with FileNotFoundError
  if CSV_FILE pointed at a directory that didn't exist yet."""
  nested_path = tmp_path / 'nested' / 'sub' / 'MyTasks.csv'
  monkeypatch.setattr(todo_list, 'CSV_FILE', str(nested_path))

  todo_list.save_tasks([{'task': 'A task', 'eta': '2026-08-17'}])  # must not raise

  assert nested_path.exists()
  assert todo_list.load_tasks() == [{'task': 'A task', 'eta': '2026-08-17'}]


# --- load_tasks: legacy migration --------------------------------------

def test_load_tasks_migrates_legacy_rows_with_default_eta(todo_list_csv, monkeypatch):
  with open(todo_list_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Купи мляко\r\n')
    f.write('Buy bread\r\n')

  class FixedDate(real_date):
    @classmethod
    def today(cls):
      return real_date(2026, 1, 1)

  monkeypatch.setattr(todo_list, 'date', FixedDate)
  tasks = todo_list.load_tasks()

  expected_eta = '2026-01-15'  # 2026-01-01 + 14 days
  assert tasks == [
      {'task': 'Купи мляко', 'eta': expected_eta},
      {'task': 'Buy bread', 'eta': expected_eta},
  ]


def test_load_tasks_migration_persists_new_format_to_disk(todo_list_csv):
  with open(todo_list_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Legacy task\r\n')

  todo_list.load_tasks()

  with open(todo_list_csv, encoding='utf-8') as f:
    first_line = f.readline().strip()
  assert first_line == 'Number,Task,ETA'


def test_load_tasks_warns_on_extra_columns_in_legacy_format(todo_list_csv, capsys):
  with open(todo_list_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Bad,Task,WithCommas\r\n')

  tasks = todo_list.load_tasks()
  captured = capsys.readouterr()

  assert len(tasks) == 1
  assert tasks[0]['task'] == 'Bad'
  assert 'Warning' in captured.out


# --- load_tasks: malformed current-format rows --------------------------

def test_load_tasks_warns_and_skips_row_with_missing_columns(todo_list_csv, capsys):
  with open(todo_list_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Number,Task,ETA\r\n')
    f.write('1,Good task,2026-08-17\r\n')
    f.write('2,Incomplete row\r\n')  # missing ETA column

  tasks = todo_list.load_tasks()
  captured = capsys.readouterr()

  assert tasks == [{'task': 'Good task', 'eta': '2026-08-17'}]
  assert 'Warning' in captured.out


def test_load_tasks_warns_and_ignores_extra_columns_in_current_format(todo_list_csv, capsys):
  with open(todo_list_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Number,Task,ETA\r\n')
    f.write('1,Good task,2026-08-17,extra,columns\r\n')

  tasks = todo_list.load_tasks()
  captured = capsys.readouterr()

  assert tasks == [{'task': 'Good task', 'eta': '2026-08-17'}]
  assert 'Warning' in captured.out


# --- add_task ----------------------------------------------------------

def test_add_task_appends_task_with_eta(todo_list_csv, monkeypatch):
  tasks = []
  responses = iter(['Wash the car', '2026-08-20'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  todo_list.add_task(tasks)
  assert tasks == [{'task': 'Wash the car', 'eta': '2026-08-20'}]


def test_add_task_persists_to_csv(todo_list_csv, monkeypatch):
  tasks = []
  responses = iter(['Read a book', '2026-09-01'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  todo_list.add_task(tasks)
  assert todo_list.load_tasks() == [{'task': 'Read a book', 'eta': '2026-09-01'}]


def test_add_task_rejects_empty_task_then_accepts_valid(todo_list_csv, monkeypatch):
  tasks = []
  responses = iter(['   ', 'Valid task', '2026-08-20'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  todo_list.add_task(tasks)
  assert tasks == [{'task': 'Valid task', 'eta': '2026-08-20'}]


def test_add_task_rejects_invalid_eta_then_accepts_valid(todo_list_csv, monkeypatch):
  tasks = []
  responses = iter(['Valid task', 'not-a-date', '2026-08-20'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  todo_list.add_task(tasks)
  assert tasks == [{'task': 'Valid task', 'eta': '2026-08-20'}]


# --- remove_task -----------------------------------------------------

def test_remove_task_removes_correct_item_by_number(todo_list_csv, monkeypatch):
  tasks = [
      {'task': 'Task A', 'eta': '2026-08-01'},
      {'task': 'Task B', 'eta': '2026-08-02'},
      {'task': 'Task C', 'eta': '2026-08-03'},
  ]
  monkeypatch.setattr('builtins.input', lambda _: '2')
  todo_list.remove_task(tasks)
  assert tasks == [
      {'task': 'Task A', 'eta': '2026-08-01'},
      {'task': 'Task C', 'eta': '2026-08-03'},
  ]


def test_remove_task_persists_to_csv(todo_list_csv, monkeypatch):
  tasks = [
      {'task': 'Task A', 'eta': '2026-08-01'},
      {'task': 'Task B', 'eta': '2026-08-02'},
  ]
  monkeypatch.setattr('builtins.input', lambda _: '1')
  todo_list.remove_task(tasks)
  assert todo_list.load_tasks() == [{'task': 'Task B', 'eta': '2026-08-02'}]


def test_remove_task_rejects_out_of_range_then_accepts_valid(todo_list_csv, monkeypatch):
  tasks = [
      {'task': 'Task A', 'eta': '2026-08-01'},
      {'task': 'Task B', 'eta': '2026-08-02'},
  ]
  responses = iter(['5', '1'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  todo_list.remove_task(tasks)
  assert tasks == [{'task': 'Task B', 'eta': '2026-08-02'}]


def test_remove_task_rejects_non_numeric_then_accepts_valid(todo_list_csv, monkeypatch):
  tasks = [{'task': 'Task A', 'eta': '2026-08-01'}]
  responses = iter(['abc', '1'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  todo_list.remove_task(tasks)
  assert tasks == []


def test_remove_task_returns_immediately_when_list_is_empty(todo_list_csv, monkeypatch):
  """Regression test: remove_task() used to loop forever asking for a
  task number when the list was empty, since no number could ever be
  in range. It should now return right away without calling input()."""
  tasks = []

  def input_should_not_be_called(_):
    raise AssertionError('input() should not be called when the task list is empty')

  monkeypatch.setattr('builtins.input', input_should_not_be_called)
  todo_list.remove_task(tasks)  # must not hang or raise
  assert tasks == []


# --- display_tasks -----------------------------------------------------

def test_display_tasks_empty_list(capsys):
  todo_list.display_tasks([])
  captured = capsys.readouterr()
  assert 'No tasks in the list.' in captured.out


def test_display_tasks_shows_header_and_rows(capsys):
  tasks = [
      {'task': 'First', 'eta': '2026-08-17'},
      {'task': 'Second', 'eta': '2026-08-20'},
  ]
  todo_list.display_tasks(tasks)
  captured = capsys.readouterr()
  assert 'Number' in captured.out
  assert 'Task' in captured.out
  assert 'ETA' in captured.out
  assert 'First' in captured.out
  assert '2026-08-17' in captured.out
  assert 'Second' in captured.out
  assert '2026-08-20' in captured.out


# --- get_choice ---------------------------------------------------------

def test_get_choice_returns_valid_choice(monkeypatch):
  monkeypatch.setattr('builtins.input', lambda _: '2')
  assert todo_list.get_choice() == '2'


def test_get_choice_rejects_invalid_then_accepts_valid(monkeypatch):
  responses = iter(['9', '4'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  assert todo_list.get_choice() == '4'


def test_get_choice_strips_surrounding_whitespace(monkeypatch):
  monkeypatch.setattr('builtins.input', lambda _: ' 2 ')
  assert todo_list.get_choice() == '2'


# --- get_eta_input -------------------------------------------------------

def test_get_eta_input_returns_valid_date(monkeypatch):
  monkeypatch.setattr('builtins.input', lambda _: '2026-08-20')
  assert todo_list.get_eta_input() == '2026-08-20'


def test_get_eta_input_rejects_invalid_format_then_accepts_valid(monkeypatch):
  responses = iter(['20-08-2026', '2026-08-20'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  assert todo_list.get_eta_input() == '2026-08-20'