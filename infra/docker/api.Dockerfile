FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY apps/api/pyproject.toml ./pyproject.toml
COPY apps/api/alembic.ini ./alembic.ini
COPY apps/api/alembic ./alembic
COPY apps/api/src ./src

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "verimed_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
