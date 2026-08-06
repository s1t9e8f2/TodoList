"""Persistence layer: reading and writing tasks to the CSV file,
including migration of files saved before the ETA column existed."""

import csv
import logging
import os
import shutil
from datetime import date, datetime, timedelta
from typing import TypedDict

logger = logging.getLogger(__name__)


class Task(TypedDict):
    task: str
    eta: str


CSV_FILE: str = "MyTasks.csv"
CSV_HEADER: list[str] = ["Number", "Task", "ETA"]
ETA_DATE_FORMAT: str = "%Y-%m-%d"
DEFAULT_ETA_DAYS: int = 14


def _default_eta() -> str:
    """ETA assigned to legacy tasks that were saved before the ETA column existed."""
    return (date.today() + timedelta(days=DEFAULT_ETA_DAYS)).strftime(ETA_DATE_FORMAT)


def _is_valid_eta(eta_text: str) -> bool:
    try:
        datetime.strptime(eta_text, ETA_DATE_FORMAT)
        return True
    except ValueError:
        return False


def _looks_like_unrecognized_header(row: list[str]) -> bool:
    """Detects a header row that uses different/incompatible columns than
    CSV_HEADER (e.g. 'Task,ETA' with no Number column), so it isn't
    silently mistaken for legacy task data and migrated incorrectly.

    Deliberately strict: ALL cells must be known column-name words, not
    just one. A legacy data row whose task text happens to contain a
    word like "task" (e.g. 'Bad,Task,WithCommas') must NOT be mistaken
    for a header - only a row that looks entirely like a header (every
    cell is one of Number/Task/ETA) is flagged."""
    normalized = [cell.strip().lower() for cell in row]
    known_header_words = {"task", "eta", "number"}
    return len(normalized) >= 1 and all(
        cell in known_header_words for cell in normalized
    )


def load_tasks() -> list[Task]:
    """Load tasks from the CSV file. If the file doesn't exist, create an
    empty one with the current header. If the file is in the old format
    (no header, one task per line, no ETA), migrate it: every task gets a
    default ETA of DEFAULT_ETA_DAYS days from today, a backup of the
    original file is created, and the migrated data is saved back
    immediately in the new format.

    Raises ValueError if the file has a header row that looks like it
    belongs to this app but doesn't match the expected columns exactly,
    instead of guessing and potentially corrupting the data.
    """
    if not os.path.exists(CSV_FILE):
        save_tasks([])
        return []

    with open(CSV_FILE, mode="r", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    if not rows:
        return []

    if rows[0] == CSV_HEADER:
        return _parse_current_format_rows(rows[1:])

    if _looks_like_unrecognized_header(rows[0]):
        raise ValueError(
            f"{CSV_FILE} has an unrecognized header row {rows[0]!r}. "
            f"Expected {CSV_HEADER!r}. Please fix the file manually, or "
            f"delete it to start with an empty list."
        )

    return _migrate_legacy_rows(rows)


def _parse_current_format_rows(data_rows: list[list[str]]) -> list[Task]:
    tasks: list[Task] = []
    for line_number, row in enumerate(data_rows, start=2):
        if not row:
            continue
        if len(row) < 3:
            logger.warning(
                "%s line %d is missing columns and will be skipped: %s",
                CSV_FILE,
                line_number,
                row,
            )
            continue
        if len(row) > 3:
            logger.warning(
                "%s line %d has extra columns that will be ignored: %s",
                CSV_FILE,
                line_number,
                row,
            )

        _, task, eta = row[0], row[1], row[2]
        task = task.strip()
        if not task:
            logger.warning(
                "%s line %d has an empty task and will be skipped.",
                CSV_FILE,
                line_number,
            )
            continue

        if not _is_valid_eta(eta):
            logger.warning(
                "%s line %d has an invalid ETA %r; using a default ETA of "
                "%d days from today instead.",
                CSV_FILE,
                line_number,
                eta,
                DEFAULT_ETA_DAYS,
            )
            eta = _default_eta()

        tasks.append({"task": task, "eta": eta})
    return tasks


def _migrate_legacy_rows(rows: list[list[str]]) -> list[Task]:
    logger.info(
        "Detected tasks without an ETA in %s - assigning a default "
        "ETA of %d calendar days from today.",
        CSV_FILE,
        DEFAULT_ETA_DAYS,
    )
    default_eta = _default_eta()

    tasks: list[Task] = []
    for line_number, row in enumerate(rows, start=1):
        if not row:
            continue
        task = row[0].strip()
        if not task:
            logger.warning(
                "%s line %d is empty and will be skipped.", CSV_FILE, line_number
            )
            continue
        if len(row) > 1:
            logger.warning(
                "%s line %d has extra columns that will be ignored: %s",
                CSV_FILE,
                line_number,
                row,
            )
        tasks.append({"task": task, "eta": default_eta})

    backup_path = CSV_FILE + ".bak"
    shutil.copy2(CSV_FILE, backup_path)
    logger.info("Backed up the original file to %s before migrating.", backup_path)

    save_tasks(tasks)  # persist the migration immediately
    return tasks


def save_tasks(tasks: list[Task]) -> None:
    """Save the current list of tasks to the CSV file, with a header row
    (Number, Task, ETA). Supports Cyrillic and Latin text via UTF-8.

    Note: the Number column is always derived from each task's current
    position in the list (1, 2, 3, ...) at save time - it is never read
    back as a persistent identifier. Removal (see tasks.remove_task) also
    works purely by list position. If Number is ever repurposed as a
    stored/looked-up identity, remove_task's index-based pop() logic
    would need to be revisited to avoid mismatches.
    """
    directory = os.path.dirname(CSV_FILE)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        for index, item in enumerate(tasks, start=1):
            writer.writerow([index, item["task"], item["eta"]])
