FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app-backend

RUN python -m venv /py && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && python -m venv /py \
    && pip install --upgrade pip \
    && pip install poetry \
    flake8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock .flake8 /app-backend/

RUN poetry install --no-root

WORKDIR /app-backend

EXPOSE 8000

RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user

RUN mkdir -p /home/django-user && \
    chown -R django-user:django-user /home/django-user

USER django-user
