"""Persistence layer: reading and writing tasks to the CSV file,
including migration of files saved before the ETA column existed."""

import csv
import os
from datetime import date, datetime, timedelta

CSV_FILE = 'MyTasks.csv'
CSV_HEADER = ['Number', 'Task', 'ETA']
ETA_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_ETA_DAYS = 14


def _default_eta():
  """ETA assigned to legacy tasks that were saved before the ETA column existed."""
  return (date.today() + timedelta(days=DEFAULT_ETA_DAYS)).strftime(ETA_DATE_FORMAT)


def load_tasks():
  """Load tasks from the CSV file. If the file doesn't exist, create an
  empty one with the current header. If the file is in the old format
  (no header, one task per line, no ETA), migrate it: every task gets a
  default ETA of DEFAULT_ETA_DAYS days from today, and the migrated data
  is saved back immediately in the new format."""
  if not os.path.exists(CSV_FILE):
    save_tasks([])
    return []

  with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
    rows = list(csv.reader(f))

  if not rows:
    return []

  if rows[0] == CSV_HEADER:
    return _parse_current_format_rows(rows[1:])

  return _migrate_legacy_rows(rows)


def _parse_current_format_rows(data_rows):
  tasks = []
  for line_number, row in enumerate(data_rows, start=2):
    if not row:
      continue
    if len(row) < 3:
      print(f'Warning: {CSV_FILE} line {line_number} is missing columns '
            f'and will be skipped: {row}')
      continue
    if len(row) > 3:
      print(f'Warning: {CSV_FILE} line {line_number} has extra columns '
            f'that will be ignored: {row}')
    _, task, eta = row[0], row[1], row[2]
    tasks.append({'task': task, 'eta': eta})
  return tasks


def _migrate_legacy_rows(rows):
  print(f'Detected tasks without an ETA in {CSV_FILE} - assigning a '
        f'default ETA of {DEFAULT_ETA_DAYS} calendar days from today.')
  default_eta = _default_eta()

  tasks = []
  for line_number, row in enumerate(rows, start=1):
    if not row:
      continue
    if len(row) > 1:
      print(f'Warning: {CSV_FILE} line {line_number} has extra columns '
            f'that will be ignored: {row}')
    tasks.append({'task': row[0], 'eta': default_eta})

  save_tasks(tasks)  # persist the migration immediately
  return tasks


def save_tasks(tasks):
  """Save the current list of tasks to the CSV file, with a header row
  (Number, Task, ETA). Supports Cyrillic and Latin text via UTF-8."""
  directory = os.path.dirname(CSV_FILE)
  if directory:
    os.makedirs(directory, exist_ok=True)

  with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(CSV_HEADER)
    for index, item in enumerate(tasks, start=1):
      writer.writerow([index, item['task'], item['eta']])
