# Advanced Calculator Application

## Project Description
This project is a command-line calculator built with object-oriented design and common software patterns.  
It supports arithmetic operations, history persistence, undo/redo, observer-based autosave/logging, and robust input validation.

### Core Features
- Arithmetic operations: `add`, `subtract`, `multiply`, `divide`, `power`, `root`, `modulus`, `int_divide`, `percentage`, `abs_diff`
- Calculation history: view, save, load, clear
- Undo/redo support via memento pattern
- Input validation and custom exception handling
- CSV-based history persistence
- Configurable behavior through environment variables
- Logging to file
- Unit tests with coverage and CI checks

## Installation Instructions
Use Python 3.12+ (project also runs in the provided local `venv`).

1. Clone and enter the project:
```bash
cd /Users/nafisha/Documents/IS601/midterm
```

2. Create a virtual environment:
```bash
python3 -m venv venv
```

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration Setup
Configuration is loaded from `.env` using `python-dotenv`.

1. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

If `.env.example` does not exist, create `.env` manually.

2. Add environment variables (example):
```env
CALCULATOR_BASE_DIR=/Users/nafisha/Documents/IS601/midterm
CALCULATOR_MAX_HISTORY_SIZE=1000
CALCULATOR_AUTO_SAVE=true
CALCULATOR_PRECISION=10
CALCULATOR_MAX_INPUT_VALUE=1e999
CALCULATOR_DEFAULT_ENCODING=utf-8
CALCULATOR_LOG_DIR=/Users/nafisha/Documents/IS601/midterm/logs
CALCULATOR_LOG_FILE=/Users/nafisha/Documents/IS601/midterm/logs/calculator.log
CALCULATOR_HISTORY_DIR=/Users/nafisha/Documents/IS601/midterm/history
CALCULATOR_HISTORY_FILE=/Users/nafisha/Documents/IS601/midterm/history/calculator_history.csv
```

3. Logging setup notes:
- Logs are written to `CALCULATOR_LOG_FILE`.
- If not set, defaults are derived from `CALCULATOR_BASE_DIR`.
- Log directories are created automatically at runtime.

## Usage Guide
Run the calculator REPL:
```bash
python main.py
```

Inside the REPL, use:
- `help` to print available commands
- `add`, `subtract`, `multiply`, `divide`, `power`, `root`, `modulus`, `int_divide`, `percentage`, `abs_diff` for calculations
- `history` to show saved calculations
- `undo` / `redo` to navigate history state
- `save` / `load` for persistence
- `clear` to clear history
- `exit` to quit (saves history before exit)

Example session:
```text
Enter command: power
First number: 2
Second number: 8
Result: 256
```

## Testing Instructions
Run tests:
```bash
pytest -q
```

Run tests with coverage:
```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

Enforce 100% coverage:
```bash
coverage report --fail-under=100
```

HTML coverage output is generated in `htmlcov/`.

## CI/CD Information
GitHub Actions workflow file: `.github/workflows/python-app.yml`

Workflow purpose:
- Runs on pushes and pull requests to `main`
- Sets up Python and installs dependencies from `requirements.txt`
- Executes test suite
- Fails build if coverage drops below 100%

This ensures every PR maintains a passing test suite and full coverage.

## Code Documentation Standards
To keep the codebase maintainable:
- Add meaningful docstrings for classes, functions, and methods
- Add concise comments only where logic is non-obvious
- Keep comments synchronized with actual behavior
- Document validation rules and error conditions in docstrings

The current codebase follows this style across `app/` modules and tests.
