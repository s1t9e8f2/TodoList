"""Entry point: menu loop tying storage, validation, and tasks together."""

import logging

import colorama

from storage import load_tasks
from tasks import add_task, display_tasks, edit_task, list_urgent_tasks, remove_task
from validation import get_choice

logger = logging.getLogger(__name__)


def print_menu() -> None:
    print("\nTodo List Menu:")
    print("1. View Tasks")
    print("2. Add a Task")
    print("3. Edit a Task")
    print("4. Remove a Task")
    print("5. Show Urgent Tasks")
    print("6. Exit")


def main() -> None:
    try:
        tasks = load_tasks()
    except ValueError as error:
        logger.error(str(error))
        return

    while True:
        print_menu()

        choice = get_choice()

        if choice == "1":
            display_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            edit_task(tasks)
        elif choice == "4":
            remove_task(tasks)
        elif choice == "5":
            list_urgent_tasks(tasks)
        else:
            break


if __name__ == "__main__":
    # Required on Windows so ANSI color codes (used for the overdue-task
    # warning in list_urgent_tasks) render correctly instead of printing
    # as raw escape sequences. Harmless no-op on Linux/macOS.
    colorama.init(autoreset=True)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C raises KeyboardInterrupt; Ctrl+D (Unix) / Ctrl+Z (Windows) or
        # a closed/exhausted input stream raises EOFError from input(). Exit
        # quietly instead of printing a raw traceback.
        print("\nExiting...")
