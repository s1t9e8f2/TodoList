"""User-input validation: menu choices and ETA dates."""

from datetime import datetime

from storage import ETA_DATE_FORMAT


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
