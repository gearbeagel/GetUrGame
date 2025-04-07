FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && apt-get install -y --no-install-recommends \
      gcc \
      g++ \
      musl-dev \
      python3-dev \
      libffi-dev \
      cmake \
      make \
      && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r /app/requirements.txt

RUN apt-get purge -y --auto-remove \
      gcc \
      g++ \
      musl-dev \
      python3-dev \
      libffi-dev \
      cmake \
      make \
      && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY . /app/

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
