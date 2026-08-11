"""User-input validation: menu choices and ETA dates."""

from datetime import date, datetime

from storage import ETA_DATE_FORMAT


def get_choice() -> str:
    while True:
        choice = input("Enter your choice: ").strip()
        valid_choices = ("1", "2", "3", "4", "5", "6")
        if choice not in valid_choices:
            print("Invalid choice")
            continue
        else:
            return choice


def get_eta_input() -> str:
    """Ask the user for an ETA date, validate its format, and require it
    to be today or a future date (a past ETA is rejected as a likely
    mistake)."""
    while True:
        eta_text = input("Enter ETA (YYYY-MM-DD): ").strip()

        try:
            parsed_date = datetime.strptime(eta_text, ETA_DATE_FORMAT).date()
        except ValueError:
            print("Invalid date format! Please use YYYY-MM-DD.")
            continue

        if parsed_date < date.today():
            print("ETA cannot be in the past. Please enter today or a future date.")
            continue

        return eta_text


def get_days_ahead_input() -> int:
    """Ask the user how many days ahead defines the urgency window for
    list_urgent_tasks(). 0 is allowed (tasks due today or already
    overdue only); negative numbers are rejected."""
    while True:
        days_text = input("Show tasks due within how many days? ").strip()

        try:
            days = int(days_text)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if days < 0:
            print("Please enter a number of days that is 0 or greater.")
            continue

        return days
