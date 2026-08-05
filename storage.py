"""Persistence layer: reading and writing tasks to the CSV file,
including migration of files saved before the ETA column existed."""

import csv
import os
import shutil
from datetime import date, datetime, timedelta

CSV_FILE = 'MyTasks.csv'
CSV_HEADER = ['Number', 'Task', 'ETA']
ETA_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_ETA_DAYS = 14


def _default_eta():
  """ETA assigned to legacy tasks that were saved before the ETA column existed."""
  return (date.today() + timedelta(days=DEFAULT_ETA_DAYS)).strftime(ETA_DATE_FORMAT)


def _is_valid_eta(eta_text):
  try:
    datetime.strptime(eta_text, ETA_DATE_FORMAT)
    return True
  except ValueError:
    return False


def _looks_like_unrecognized_header(row):
  """Detects a header row that uses different/incompatible columns than
  CSV_HEADER (e.g. 'Task,ETA' with no Number column), so it isn't
  silently mistaken for legacy task data and migrated incorrectly."""
  normalized = [cell.strip().lower() for cell in row]
  return any(cell in ('task', 'eta', 'number') for cell in normalized)


def load_tasks():
  """Load tasks from the CSV file. If the file doesn't exist, create an
  empty one with the current header. If the file is in the old format
  (no header, one task per line, no ETA), migrate it: every task gets a
  default ETA of DEFAULT_ETA_DAYS days from today, a backup of the
  original file is created, and the migrated data is saved back
  immediately in the new format.

  Raises ValueError if the file has a header row that looks like it
  belongs to this app but doesn't match the expected columns exactly,
  instead of guessing and potentially corrupting the data.
  """
  if not os.path.exists(CSV_FILE):
    save_tasks([])
    return []

  with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
    rows = list(csv.reader(f))

  if not rows:
    return []

  if rows[0] == CSV_HEADER:
    return _parse_current_format_rows(rows[1:])

  if _looks_like_unrecognized_header(rows[0]):
    raise ValueError(
        f'{CSV_FILE} has an unrecognized header row {rows[0]!r}. '
        f'Expected {CSV_HEADER!r}. Please fix the file manually, or '
        f'delete it to start with an empty list.'
    )

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
    task = task.strip()
    if not task:
      print(f'Warning: {CSV_FILE} line {line_number} has an empty task '
            f'and will be skipped.')
      continue

    if not _is_valid_eta(eta):
      print(f'Warning: {CSV_FILE} line {line_number} has an invalid ETA '
            f'{eta!r}; using a default ETA of {DEFAULT_ETA_DAYS} days '
            f'from today instead.')
      eta = _default_eta()

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
    task = row[0].strip()
    if not task:
      print(f'Warning: {CSV_FILE} line {line_number} is empty and will '
            f'be skipped.')
      continue
    if len(row) > 1:
      print(f'Warning: {CSV_FILE} line {line_number} has extra columns '
            f'that will be ignored: {row}')
    tasks.append({'task': task, 'eta': default_eta})

  backup_path = CSV_FILE + '.bak'
  shutil.copy2(CSV_FILE, backup_path)
  print(f'Backed up the original file to {backup_path} before migrating.')

  save_tasks(tasks)  # persist the migration immediately
  return tasks


def save_tasks(tasks):
  """Save the current list of tasks to the CSV file, with a header row
  (Number, Task, ETA). Supports Cyrillic and Latin text via UTF-8.

  Note: the Number column is always derived from each task's current
  position in the list (1, 2, 3, ...) at save time - it is never read
  back as a persistent identifier. Removal (see tasks.remove_task) also
  works purely by list position. If Number is ever repurposed as a
  stored/looked-up identity, remove_task's index-based pop() logic
  would need to be revisited to avoid mismatches.
  """
  directory = os.path.dirname(CSV_FILE)
  if directory:
    os.makedirs(directory, exist_ok=True)

  with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(CSV_HEADER)
    for index, item in enumerate(tasks, start=1):
      writer.writerow([index, item['task'], item['eta']])
