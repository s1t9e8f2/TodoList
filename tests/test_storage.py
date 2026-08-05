"""
Regression tests for storage.py (pytest version).

Install pytest first:
    pip install pytest

Run from the project root with:
    pytest tests/test_storage_pytest.py -v
"""

import os

import pytest
from datetime import date as real_date

import storage


@pytest.fixture
def storage_csv(tmp_path, monkeypatch):
  """Point CSV_FILE at a temporary file for the duration of a test."""
  csv_path = tmp_path / 'MyTasks.csv'
  monkeypatch.setattr(storage, 'CSV_FILE', str(csv_path))
  return str(csv_path)


# --- basics --------------------------------------------------------------

def test_load_tasks_creates_empty_file_with_header_if_missing(storage_csv):
  assert not os.path.exists(storage_csv)
  tasks = storage.load_tasks()
  assert tasks == []

  with open(storage_csv, encoding='utf-8') as f:
    first_line = f.readline().strip()
  assert first_line == 'Number,Task,ETA'


def test_save_tasks_writes_header_and_rows(storage_csv):
  """Tests save_tasks() in isolation by reading the raw bytes on disk,
  instead of trusting load_tasks() to read them back correctly."""
  storage.save_tasks([
      {'task': 'Купи мляко', 'eta': '2026-08-17'},
      {'task': 'Buy bread', 'eta': '2026-08-20'},
  ])

  with open(storage_csv, mode='rb') as f:
    raw_bytes = f.read()

  expected = (
      'Number,Task,ETA\r\n'
      '1,Купи мляко,2026-08-17\r\n'
      '2,Buy bread,2026-08-20\r\n'
  ).encode('utf-8')
  assert raw_bytes == expected


def test_load_tasks_reads_existing_current_format_rows(storage_csv):
  """Tests load_tasks() in isolation by writing the file content by
  hand, instead of trusting save_tasks() to have written it."""
  with open(storage_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Number,Task,ETA\r\n')
    f.write('1,Купи мляко,2026-08-17\r\n')
    f.write('2,Buy bread,2026-08-20\r\n')

  tasks = storage.load_tasks()
  assert tasks == [
      {'task': 'Купи мляко', 'eta': '2026-08-17'},
      {'task': 'Buy bread', 'eta': '2026-08-20'},
  ]


def test_save_and_load_roundtrip(storage_csv):
  original = [
      {'task': 'Купи мляко', 'eta': '2026-08-17'},
      {'task': 'Buy bread', 'eta': '2026-08-20'},
  ]
  storage.save_tasks(original)
  assert storage.load_tasks() == original


def test_save_tasks_creates_missing_parent_directory(tmp_path, monkeypatch):
  """Regression test: save_tasks() used to crash with FileNotFoundError
  if CSV_FILE pointed at a directory that didn't exist yet."""
  nested_path = tmp_path / 'nested' / 'sub' / 'MyTasks.csv'
  monkeypatch.setattr(storage, 'CSV_FILE', str(nested_path))

  storage.save_tasks([{'task': 'A task', 'eta': '2026-08-17'}])  # must not raise

  assert nested_path.exists()
  assert storage.load_tasks() == [{'task': 'A task', 'eta': '2026-08-17'}]


# --- legacy migration ------------------------------------------------

def test_load_tasks_migrates_legacy_rows_with_default_eta(storage_csv, monkeypatch):
  with open(storage_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Купи мляко\r\n')
    f.write('Buy bread\r\n')

  class FixedDate(real_date):
    @classmethod
    def today(cls):
      return real_date(2026, 1, 1)

  monkeypatch.setattr(storage, 'date', FixedDate)
  tasks = storage.load_tasks()

  expected_eta = '2026-01-15'  # 2026-01-01 + 14 days
  assert tasks == [
      {'task': 'Купи мляко', 'eta': expected_eta},
      {'task': 'Buy bread', 'eta': expected_eta},
  ]


def test_load_tasks_migration_persists_new_format_to_disk(storage_csv):
  with open(storage_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Legacy task\r\n')

  storage.load_tasks()

  with open(storage_csv, encoding='utf-8') as f:
    first_line = f.readline().strip()
  assert first_line == 'Number,Task,ETA'


def test_load_tasks_warns_on_extra_columns_in_legacy_format(storage_csv, capsys):
  with open(storage_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Bad,Task,WithCommas\r\n')

  tasks = storage.load_tasks()
  captured = capsys.readouterr()

  assert len(tasks) == 1
  assert tasks[0]['task'] == 'Bad'
  assert 'Warning' in captured.out


def test_load_tasks_migration_creates_backup_file(storage_csv):
  """Regression test: migrating a legacy file used to overwrite it
  immediately with no way to recover the original content. A .bak copy
  of the original file must now be created first."""
  with open(storage_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Legacy task\r\n')

  storage.load_tasks()

  backup_path = storage_csv + '.bak'
  assert os.path.exists(backup_path)
  with open(backup_path, encoding='utf-8') as f:
    assert f.read() == 'Legacy task\n'


# --- ambiguous / unrecognized header -----------------------------------

def test_load_tasks_raises_on_unrecognized_header(storage_csv):
  """Regression test: a header using different columns (e.g. 'Task,ETA'
  with no Number column) used to be silently treated as legacy data,
  corrupting real ETA values with the default. It must now raise a
  clear error instead of guessing."""
  with open(storage_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Task,ETA\r\n')
    f.write('Buy milk,2026-08-03\r\n')

  with pytest.raises(ValueError, match='unrecognized header'):
    storage.load_tasks()


# --- malformed current-format rows --------------------------------------

def test_load_tasks_warns_and_skips_row_with_missing_columns(storage_csv, capsys):
  with open(storage_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Number,Task,ETA\r\n')
    f.write('1,Good task,2026-08-17\r\n')
    f.write('2,Incomplete row\r\n')  # missing ETA column

  tasks = storage.load_tasks()
  captured = capsys.readouterr()

  assert tasks == [{'task': 'Good task', 'eta': '2026-08-17'}]
  assert 'Warning' in captured.out


def test_load_tasks_warns_and_ignores_extra_columns_in_current_format(storage_csv, capsys):
  with open(storage_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Number,Task,ETA\r\n')
    f.write('1,Good task,2026-08-17,extra,columns\r\n')

  tasks = storage.load_tasks()
  captured = capsys.readouterr()

  assert tasks == [{'task': 'Good task', 'eta': '2026-08-17'}]
  assert 'Warning' in captured.out


def test_load_tasks_warns_and_defaults_invalid_eta(storage_csv, capsys):
  """Regression test: an invalid/unparseable ETA used to be loaded
  as-is with no validation. It must now be replaced with a default
  ETA and a warning printed."""
  with open(storage_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Number,Task,ETA\r\n')
    f.write('1,Good task,not-a-date\r\n')

  tasks = storage.load_tasks()
  captured = capsys.readouterr()

  assert len(tasks) == 1
  assert tasks[0]['task'] == 'Good task'
  assert tasks[0]['eta'] != 'not-a-date'
  assert 'Warning' in captured.out
  assert 'invalid ETA' in captured.out


def test_load_tasks_skips_row_with_empty_task(storage_csv, capsys):
  """Regression test: a row with an empty task (e.g. ',,2026-08-03' or
  a hand-edited blank cell) used to be loaded as a blank task. It
  should now be skipped with a warning."""
  with open(storage_csv, mode='w', newline='', encoding='utf-8') as f:
    f.write('Number,Task,ETA\r\n')
    f.write('1,,2026-08-03\r\n')
    f.write('2,Real task,2026-08-04\r\n')

  tasks = storage.load_tasks()
  captured = capsys.readouterr()

  assert tasks == [{'task': 'Real task', 'eta': '2026-08-04'}]
  assert 'Warning' in captured.out
