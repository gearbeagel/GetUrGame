FROM python:3.12
LABEL maintainer="kondr"

ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    gcc \
    && pip install --upgrade pip \
    && pip install poetry \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-root --no-interaction

WORKDIR /app/backend

RUN adduser --disabled-password --no-create-home django-user && \
    chown -R django-user:django-user /app

USER django-user
