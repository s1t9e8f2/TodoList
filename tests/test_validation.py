"""
Regression tests for validation.py (pytest version).

Install pytest first:
    pip install pytest

Run from the project root with:
    pytest tests/test_validation.py -v
"""

import validation

# --- get_choice ---------------------------------------------------------

def test_get_choice_returns_valid_choice(monkeypatch):
  monkeypatch.setattr('builtins.input', lambda _: '2')
  assert validation.get_choice() == '2'


def test_get_choice_rejects_invalid_then_accepts_valid(monkeypatch):
  responses = iter(['9', '4'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  assert validation.get_choice() == '4'


def test_get_choice_strips_surrounding_whitespace(monkeypatch):
  monkeypatch.setattr('builtins.input', lambda _: ' 2 ')
  assert validation.get_choice() == '2'


# --- get_eta_input -------------------------------------------------------

def test_get_eta_input_returns_valid_future_date(monkeypatch):
  monkeypatch.setattr('builtins.input', lambda _: '2099-01-01')
  assert validation.get_eta_input() == '2099-01-01'


def test_get_eta_input_rejects_invalid_format_then_accepts_valid(monkeypatch):
  responses = iter(['20-08-2026', '2099-01-01'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  assert validation.get_eta_input() == '2099-01-01'


def test_get_eta_input_rejects_past_date_then_accepts_valid(monkeypatch):
  """Regression test: get_eta_input() used to accept any validly
  formatted date, including ones in the past. It should now reject
  past dates and re-prompt."""
  responses = iter(['2020-01-01', '2099-01-01'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  assert validation.get_eta_input() == '2099-01-01'


def test_get_eta_input_accepts_todays_date(monkeypatch):
  from datetime import date
  today_text = date.today().strftime('%Y-%m-%d')
  monkeypatch.setattr('builtins.input', lambda _: today_text)
  assert validation.get_eta_input() == today_text
