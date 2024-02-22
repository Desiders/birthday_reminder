FROM python:3.11-slim-buster as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

ENV PATH="/opt/venv/bin:$PATH"

FROM python-base as builder-base
RUN apt-get update \
 && apt-get install -y git

RUN python3 -m venv /opt/venv
WORKDIR /build
COPY ./pyproject.toml /build
COPY ./src /build/src
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir setuptools wheel \
 && pip install --no-cache-dir /build

FROM python-base as production
COPY --from=builder-base /opt/venv /opt/venv

WORKDIR /app
COPY ./src /app/src
WORKDIR /app/src

CMD ["python", "-Om", "birthday_reminder"]
