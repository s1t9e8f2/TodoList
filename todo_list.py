import csv
import os
from datetime import date, datetime, timedelta

CSV_FILE = 'MyTasks.csv'
CSV_HEADER = ['Number', 'Task', 'ETA']
ETA_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_ETA_DAYS = 14


def print_menu():
  print('\nTodo List Menu:')
  print('1. View Tasks')
  print('2. Add a Task')
  print('3. Remove a Task')
  print('4. Exit')


def get_choice():
  while True:
    choice = input('Enter your choice: ').strip()
    valid_choices = ('1', '2', '3', '4')
    if choice not in valid_choices:
      print('Invalid choice')
      continue
    else:
      return choice


def get_eta_input():
  """Ask the user for an ETA date and validate its format."""
  while True:
    eta_text = input('Enter ETA (YYYY-MM-DD): ').strip()
    try:
      datetime.strptime(eta_text, ETA_DATE_FORMAT)
      return eta_text
    except ValueError:
      print('Invalid date format! Please use YYYY-MM-DD.')


def display_tasks(tasks):
  if not tasks:
    print('No tasks in the list.')
    return

  print(f'{"Number":<8}{"Task":<30}{"ETA":<12}')
  for index, item in enumerate(tasks, start=1):
    print(f'{index:<8}{item["task"]:<30}{item["eta"]:<12}')


def add_task(tasks):
  while True:
    task_text = input('Enter a new task: ').strip()
    if len(task_text) != 0:
      break
    else:
      print('Invalid task!')

  eta = get_eta_input()
  tasks.append({'task': task_text, 'eta': eta})
  save_tasks(tasks)


def remove_task(tasks):
  display_tasks(tasks)

  if not tasks:
    return

  while True:
    try:
      task_number = int(input('Enter the task number: '))
      if 1 <= task_number <= len(tasks):
        tasks.pop(task_number - 1)
        save_tasks(tasks)
        break
      else:
        raise ValueError
    except ValueError:
      print('Invalid task number')


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


def main():
  tasks = load_tasks()

  while True:
    print_menu()

    choice = get_choice()

    if choice == '1':
      display_tasks(tasks)
    elif choice == '2':
      add_task(tasks)
    elif choice == '3':
      remove_task(tasks)
    else:
      break


if __name__ == '__main__':
  main()