# birthday_reminder
Telegram bot to remind you of friends' birthdays

## Installation
- Install [Docker](https://docs.docker.com/get-docker/), [Docker Compose](https://docs.docker.com/compose/install/) and [just](https://github.com/casey/just#installation)
- Clone this repository `git clone https://github.com/Desiders/birthday_reminder.git`
- Copy `.env.example` to `.env` and fill it with your data

## Running and stopping the application
Before running the bot you need to run migrations. To do this run the following command:

```bash
just migration-docker
```

or without `just`:

```bash
docker compose --profile migration up --build
```

To start the bot run the following command:

```bash
just run-docker
```

or without `just`:

```bash
docker compose --profile bot up --build
```

To stop the bot run the following command:

```bash
just stop-docker
```

or without `just`:

```bash
docker compose stop bot postgres postgres_migration
```

## Development
Check other commands in the `justfile` to run tests, linters, etc.

```bash
just help
```
