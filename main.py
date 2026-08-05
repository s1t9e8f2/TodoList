"""Entry point: menu loop tying storage, validation, and tasks together."""

from storage import load_tasks
from validation import get_choice
from tasks import display_tasks, add_task, remove_task


def print_menu():
  print('\nTodo List Menu:')
  print('1. View Tasks')
  print('2. Add a Task')
  print('3. Remove a Task')
  print('4. Exit')


def main():
  try:
    tasks = load_tasks()
  except ValueError as error:
    print(f'Error: {error}')
    return

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
  try:
    main()
  except (KeyboardInterrupt, EOFError):
    # Ctrl+C raises KeyboardInterrupt; Ctrl+D (Unix) / Ctrl+Z (Windows) or
    # a closed/exhausted input stream raises EOFError from input(). Exit
    # quietly instead of printing a raw traceback.
    print('\nExiting...')
