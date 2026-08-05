"""
Regression tests for validation.py (pytest version).

Install pytest first:
    pip install pytest

Run from the project root with:
    pytest tests/test_validation_pytest.py -v
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

def test_get_eta_input_returns_valid_date(monkeypatch):
  monkeypatch.setattr('builtins.input', lambda _: '2026-08-20')
  assert validation.get_eta_input() == '2026-08-20'


def test_get_eta_input_rejects_invalid_format_then_accepts_valid(monkeypatch):
  responses = iter(['20-08-2026', '2026-08-20'])
  monkeypatch.setattr('builtins.input', lambda _: next(responses))
  assert validation.get_eta_input() == '2026-08-20'
