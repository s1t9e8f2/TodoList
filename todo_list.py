import csv
import os

CSV_FILE = 'MyTasks.csv'


def print_menu():
  print('\nTodo List Menu:')
  print('1. View Tasks')
  print('2. Add a Task')
  print('3. Remove a Task')
  print('4. Exit')


def get_choice():
  while True:
    choice = input('Enter your choice: ')
    valid_choices = ('1', '2', '3', '4')
    if choice not in valid_choices:
      print('Invalid choice')
      continue
    else:
      return choice


def display_tasks(tasks):
  if not tasks:
    print('No tasks in the list.')
    return

  for index, task in enumerate(tasks, start=1):
    print(f'{index}. {task}')


def add_task(tasks):
  while True:
    task = input('Enter a new task: ').strip()
    if len(task) != 0:
      tasks.append(task)
      save_tasks(tasks)
      break
    else:
      print('Invalid task!')


def remove_task(tasks):
  display_tasks(tasks)

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


def load_tasks():
  """Load tasks from the CSV file. If the file doesn't exist, create an empty one."""
  tasks = []

  if not os.path.exists(CSV_FILE):
    save_tasks(tasks)
    return tasks

  with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
      if row:
        tasks.append(row[0])

  return tasks


def save_tasks(tasks):
  """Save the current list of tasks to the CSV file (supports Cyrillic and Latin text via UTF-8)."""
  with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    for task in tasks:
      writer.writerow([task])


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