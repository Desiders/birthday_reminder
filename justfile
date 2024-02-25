host := `uname -a`

# Show help message
help:
    just -l

# Run bot in docker container
run-docker:
	docker compose --profile bot up --build

# Stop bot
stop-docker:
    docker compose stop bot postgres postgres_migration

# Run database migration in docker container
migration-docker:
	docker compose --profile migration up --build

# Down docker
down-docker:
	docker compose --profile bot down

# Build docker image
build-docker:
	docker compose build bot postgres postgres_migration

set dotenv-load

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

# Run ruff linter check with `pyproject.toml` configuration and fix issues
# and run ruff formatter
ruff:
    source .venv/bin/activate && \
    ruff check --config=pyproject.toml --fix . || \
    ruff format --config=pyproject.toml .

# Run database migration
alembic-upgrade-head:
    source .venv/bin/activate && \
    alembic upgrade head

# Run database migration with revision
alembic-upgrade-revision REVISION:
    source .venv/bin/activate && \
    alembic upgrade {{REVISION}}

# Run database migration with relative revision
alembic-upgrade-relative REVISION:
    source .venv/bin/activate && \
    alembic upgrade +{{REVISION}}

# Run database migration
alembic-downgrade-base:
    source .venv/bin/activate && \
    alembic downgrade base

# Run database migration with revision
alembic-downgrade REVISION:
    source .venv/bin/activate && \
    alembic downgrade {{REVISION}}

# Run database migration with relative revision
alembic-downgrade-relative REVISION:
    source .venv/bin/activate && \
    alembic downgrade -{{REVISION}}

# Run autogenerate migration with `-m` message
alembic-autogenerate MESSAGE:
    source .venv/bin/activate && \
    alembic revision --autogenerate -m {{MESSAGE}}
