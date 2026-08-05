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
