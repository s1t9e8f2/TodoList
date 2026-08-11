"""Task operations: adding, removing, and displaying tasks."""

from datetime import date, datetime, timedelta

from storage import ETA_DATE_FORMAT, Task, save_tasks
from validation import get_days_ahead_input, get_eta_input


def display_tasks(tasks: list[Task]) -> None:
    if not tasks:
        print("No tasks in the list.")
        return

    print(f"{'Number':<8}{'Task':<30}{'ETA':<12}")
    for index, item in enumerate(tasks, start=1):
        print(f"{index:<8}{item['task']:<30}{item['eta']:<12}")


def list_urgent_tasks(tasks: list[Task]) -> None:
    """Ask the user for a number of days ahead, then show every task due
    within that window - including any already-overdue tasks, since
    those are the most urgent of all - sorted soonest-first. Shows a
    visible warning banner if any matching task is overdue."""
    if not tasks:
        print("No tasks in the list.")
        return

    days_ahead = get_days_ahead_input()
    today = date.today()
    cutoff = today + timedelta(days=days_ahead)

    matching = [
        item
        for item in tasks
        if datetime.strptime(item["eta"], ETA_DATE_FORMAT).date() <= cutoff
    ]

    if not matching:
        print(f"No tasks due within the next {days_ahead} day(s).")
        return

    matching.sort(key=lambda item: item["eta"])

    overdue = [
        item
        for item in matching
        if datetime.strptime(item["eta"], ETA_DATE_FORMAT).date() < today
    ]
    if overdue:
        print(f"\n*** WARNING: {len(overdue)} task(s) are OVERDUE! ***\n")

    print(f"{'Task':<30}{'ETA':<12}{'Status':<10}")
    for item in matching:
        eta_date = datetime.strptime(item["eta"], ETA_DATE_FORMAT).date()
        status = "OVERDUE" if eta_date < today else ""
        print(f"{item['task']:<30}{item['eta']:<12}{status:<10}")


def add_task(tasks: list[Task]) -> None:
    while True:
        task_text = input("Enter a new task: ").strip()
        if len(task_text) != 0:
            break
        else:
            print("Invalid task!")

    eta = get_eta_input()
    tasks.append({"task": task_text, "eta": eta})
    save_tasks(tasks)


def edit_task(tasks: list[Task]) -> None:
    display_tasks(tasks)

    if not tasks:
        return

    while True:
        try:
            task_number = int(input("Enter the task number to edit: "))
            if 1 <= task_number <= len(tasks):
                # Same position-based lookup as remove_task() - see the note
                # there about Number always matching the current list order.
                break
            else:
                raise ValueError
        except ValueError:
            print("Invalid task number")

    item = tasks[task_number - 1]

    print(f"Current task: {item['task']}")
    new_text = input("Enter new task text (leave blank to keep current): ").strip()
    if new_text:
        item["task"] = new_text

    print(f"Current ETA: {item['eta']}")
    while True:
        change_eta = input("Change ETA? (y/n): ").strip().lower()
        if change_eta in ("y", "n"):
            break
        print("Invalid choice. Please enter y or n.")

    if change_eta == "y":
        item["eta"] = get_eta_input()

    save_tasks(tasks)


def remove_task(tasks: list[Task]) -> None:
    display_tasks(tasks)

    if not tasks:
        return

    while True:
        try:
            task_number = int(input("Enter the task number: "))
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
            print("Invalid task number")
