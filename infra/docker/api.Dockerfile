FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system verimed \
    && useradd --system --gid verimed --create-home verimed

COPY apps/api/pyproject.toml ./pyproject.toml
COPY apps/api/requirements.lock ./requirements.lock
COPY apps/api/alembic.ini ./alembic.ini
COPY apps/api/alembic ./alembic
COPY apps/api/src ./src

ARG INSTALL_ML=false

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./requirements.lock && \
    if [ "$INSTALL_ML" = "true" ]; then pip install --no-cache-dir -e ".[ml]"; else pip install --no-cache-dir -e .; fi && \
    chown -R verimed:verimed /app

USER verimed

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/v1/health/live || exit 1

CMD ["uvicorn", "verimed_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
