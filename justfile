set dotenv-load

host := `uname -a`

# Init `.venv` virtual environment
init-venv:
    python3 -m venv .venv && \
    source .venv/bin/activate && \
    pip install .[test,lint,dev]

# Run bot in `.venv` virtual environment
run:
    source .venv/bin/activate && \
    python -m birthday_reminder

# Run ruff linter check with `pyproject.toml` configuration and fix issues
ruff-lint:
    source .venv/bin/activate && \
    ruff check --config=pyproject.toml --fix . 

# Run ruff formatter with `pyproject.toml` configuration
ruff-format:
    source .venv/bin/activate && \
    ruff format --config=pyproject.toml .
