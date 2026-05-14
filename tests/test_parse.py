from datetime import date
from nldate import parse

TODAY = date(2025, 3, 15)  # A Saturday, useful for weekday tests

# --- Absolute dates ---
def test_absolute_month_name():
    assert parse("December 1st, 2025") == date(2025, 12, 1)

def test_absolute_no_ordinal():
    assert parse("January 5 2024") == date(2024, 1, 5)

def test_absolute_short_month():
    assert parse("Mar 20, 2025") == date(2025, 3, 20)

# --- Simple relative ---
def test_today():
    assert parse("today", today=TODAY) == TODAY

def test_tomorrow():
    assert parse("tomorrow", today=TODAY) == date(2025, 3, 16)

def test_yesterday():
    assert parse("yesterday", today=TODAY) == date(2025, 3, 14)

# --- Offset from today ---
def test_days_from_now():
    assert parse("5 days from now", today=TODAY) == date(2025, 3, 20)

def test_weeks_ago():
    assert parse("2 weeks ago", today=TODAY) == date(2025, 3, 1)

def test_months_from_now():
    assert parse("3 months from now", today=TODAY) == date(2025, 6, 15)

def test_one_year_ago():
    assert parse("1 year ago", today=TODAY) == date(2024, 3, 15)

# --- Offset from an anchor date ---
def test_days_before_anchor():
    assert parse("5 days before December 1st, 2025") == date(2025, 11, 26)

def test_days_after_anchor():
    assert parse("10 days after March 1st, 2025") == date(2025, 3, 11)

def test_year_and_months_after_anchor():
    assert parse("1 year and 2 months after January 1st, 2025") == date(2026, 3, 1)

# --- Weekday expressions ---
def test_next_tuesday():
    assert parse("next Tuesday", today=TODAY) == date(2025, 3, 18)

def test_last_monday():
    assert parse("last Monday", today=TODAY) == date(2025, 3, 10)

def test_next_saturday_is_next_week():
    assert parse("next Saturday", today=TODAY) == date(2025, 3, 22)