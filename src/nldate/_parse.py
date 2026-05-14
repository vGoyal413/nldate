from datetime import date, timedelta
import re

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

UNITS = {"day": 1, "week": 7, "month": 0, "year": 0}


def _parse_absolute(s: str) -> date | None:
    """Try to parse an absolute date like 'December 1st, 2025' or 'Jan 5 2024'."""
    s = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", s)
    pattern = r"([a-zA-Z]+)\s+(\d{1,2}),?\s+(\d{4})"
    m = re.match(pattern, s.strip(), re.IGNORECASE)
    if m:
        month_str, day_str, year_str = m.groups()
        month = MONTHS.get(month_str.lower().rstrip("."))
        if month:
            return date(int(year_str), month, int(day_str))
    return None


def _add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(
        d.day,
        [31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][
            month - 1
        ],
    )
    return date(year, month, day)


def _apply_offset(base: date, quantity: int, unit: str, direction: int) -> date:
    """Apply an offset to a base date. direction is +1 or -1."""
    unit = unit.rstrip("s")  # normalize plural
    if unit == "day":
        return base + timedelta(days=direction * quantity)
    elif unit == "week":
        return base + timedelta(weeks=direction * quantity)
    elif unit == "month":
        return _add_months(base, direction * quantity)
    elif unit == "year":
        return _add_months(base, direction * quantity * 12)
    return base


def parse(s: str, today: date | None = None) -> date:
    today_: date = today if today is not None else date.today()  # type: ignore[assignment]

    s = s.strip().lower()

    if s == "today":
        return today_
    if s == "tomorrow":
        return today_ + timedelta(days=1)
    if s == "yesterday":
        return today_ + timedelta(days=-1)

    # --- Next/last weekday ---
    m = re.match(
        r"(next|last)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", s
    )
    if m:
        direction, weekday_str = m.groups()
        target = WEEKDAYS[weekday_str]
        current = today_.weekday()
        if direction == "next":
            days_ahead = (target - current) % 7
            if days_ahead == 0:
                days_ahead = 7
            return today_ + timedelta(days=days_ahead)
        else:
            days_behind = (current - target) % 7
            if days_behind == 0:
                days_behind = 7
            return today_ + timedelta(days=-days_behind)

    # --- Offset from an anchor: "5 days before December 1st, 2025" ---
    m = re.match(r"(\d+)\s+(days?|weeks?|months?|years?)\s+(before|after)\s+(.+)", s)
    if m:
        qty, unit, direction_str, anchor_str = m.groups()
        anchor = parse(anchor_str.strip(), today=today_)
        direction = 1 if direction_str == "after" else -1
        return _apply_offset(anchor, int(qty), unit, direction)

    # --- Compound offset: "1 year and 2 months after January 1st, 2025" ---
    m = re.match(
        r"(\d+)\s+(years?)\s+and\s+(\d+)\s+(months?)\s+(before|after)\s+(.+)", s
    )
    if m:
        y_qty, _, mo_qty, _, direction_str, anchor_str = m.groups()
        anchor = parse(anchor_str.strip(), today=today_)
        direction = 1 if direction_str == "after" else -1
        result = _apply_offset(anchor, int(y_qty), "year", direction)
        result = _apply_offset(result, int(mo_qty), "month", direction)
        return result

    # --- Offset from now: "5 days from now", "2 weeks ago", "3 months from now" ---
    m = re.match(r"(\d+)\s+(days?|weeks?|months?|years?)\s+(from now|ago)", s)
    if m:
        qty, unit, direction_str = m.groups()
        direction = 1 if direction_str == "from now" else -1
        return _apply_offset(today_, int(qty), unit, direction)

    # --- ISO format: "2025-12-04" ---
    m = re.match(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})$", s)
    if m:
        year, month, day = m.groups()
        return date(int(year), int(month), int(day))

    # --- US format: "12/04/2025" (month/day/year) ---
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        month, day, year = m.groups()
        return date(int(year), int(month), int(day))

    # --- "in X days/weeks/months/years" ---
    m = re.match(r"in\s+(\d+)\s+(days?|weeks?|months?|years?)", s)
    if m:
        qty, unit = m.groups()
        return _apply_offset(today_, int(qty), unit, 1)

    # --- "X days/weeks/months/years later" ---
    m = re.match(r"(\d+)\s+(days?|weeks?|months?|years?)\s+later", s)
    if m:
        qty, unit = m.groups()
        return _apply_offset(today_, int(qty), unit, 1)

    # --- Absolute date as fallback ---
    absolute = _parse_absolute(s)
    if absolute:
        return absolute

    raise ValueError(f"Could not parse date string: {s!r}")
