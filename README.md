# Todo List CLI

A simple command-line todo list application with CSV persistence and ETA (due date) tracking.

## Features

- View, add, edit, and remove tasks from the command line
- Each task has a text description and an ETA (due date)
- Tasks are automatically saved to `MyTasks.csv` (Number, Task, ETA columns)
- Supports both Cyrillic and Latin text
- Automatically migrates older CSV files (saved before the ETA column existed), assigning a default ETA and backing up the original file first

## Requirements

- Python 3.10+
- No runtime dependencies (uses only the standard library)

## Usage

```bash
python3 main.py
```

You'll see a menu:

```
Todo List Menu:
1. View Tasks
2. Add a Task
3. Edit a Task
4. Remove a Task
5. Exit
```

Tasks are saved to `MyTasks.csv` in the current directory. This file is created automatically the first time you run the app.

## Project Structure

```
project/
├── main.py           # Entry point: menu loop
├── storage.py         # CSV persistence: load_tasks, save_tasks, legacy migration
├── tasks.py            # Task operations: add_task, remove_task, display_tasks
├── validation.py        # Input validation: get_choice, get_eta_input
├── pyproject.toml        # pytest, mypy, and ruff configuration
├── requirements.txt   # Development/testing dependencies
├── .gitignore
└── tests/
    ├── conftest.py         # Makes the project root importable from tests/
    ├── test_storage.py
    ├── test_tasks.py
    └── test_validation.py
```

## Development setup

```bash
pip install -r requirements.txt
```

## Running tests

```bash
pytest -v
```

This runs the test suite along with automatic **mypy** (type checking) and **ruff** (linting) checks on every file, configured in `pyproject.toml`.

### Formatting

The codebase is formatted with `ruff format` (Black-compatible, 4-space indentation, double quotes). This is enforced automatically on every `pytest -v` run via the `--ruff-format` check configured in `pyproject.toml`.

If you edit any file, re-run the formatter before committing:

```bash
ruff format .
```

## Notes

- The `Number` column in `MyTasks.csv` always reflects each task's current position in the list — it is not a persistent ID and is recalculated on every save.
- ETA dates must be in `YYYY-MM-DD` format and cannot be in the past.
