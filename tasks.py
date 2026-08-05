"""Task operations: adding, removing, and displaying tasks."""

from storage import save_tasks
from validation import get_eta_input


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
        # task_number here is the *position* shown by display_tasks(),
        # not a stored identifier - it always matches list order because
        # storage.save_tasks() also always derives Number from position.
        # If Number is ever persisted/read as a real ID, this pop()
        # logic must be updated to look it up instead of assuming it.
        tasks.pop(task_number - 1)
        save_tasks(tasks)
        break
      else:
        raise ValueError
    except ValueError:
      print('Invalid task number')
