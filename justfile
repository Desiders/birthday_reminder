set dotenv-load

host := `uname -a`

# Run bot in `.venv` virtual environment
run:
    source .venv/bin/activate
    python -m src.birthday_reminder

# Run ruff linter check with `pyproject.toml` configuration and fix issues
ruff-lint:
    ruff check --config=pyproject.toml --fix . 

# Run ruff formatter with `pyproject.toml` configuration
ruff-format:
    ruff format --config=pyproject.toml .
