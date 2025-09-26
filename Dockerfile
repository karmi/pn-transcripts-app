# $ docker build -t pn-transcriptions:latest .
# $ docker run -p 8080:8080 -e R2_ACCESS_KEY_ID=<REPLACE> -e R2_SECRET_ACCESS_KEY=<REPLACE> pn-transcriptions:latest

# ---------- Stage 1: build frontend ----------
FROM node:20-alpine AS frontend
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm clean-install

COPY frontend/ ./
RUN npm run build

# ---------- Stage 2: build Python dependencies with uv ----------
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS backend
WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

COPY backend/ backend/

RUN uv sync --frozen --no-dev

# ---------- Stage 3: runtime ----------
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  VENV_PATH=/app/.venv \
  PATH=/app/.venv/bin:$PATH

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  ca-certificates curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=backend /app/.venv /app/.venv
COPY --from=backend /app/backend /app/backend

COPY --from=frontend /app/dist frontend/dist

# Create non-root user
RUN useradd -u 10001 -r -s /usr/sbin/nologin appuser && \
  chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["gunicorn", "--chdir", "backend", "--workers", "1", "--threads", "8", "--bind", "0.0.0.0:8080", "--access-logfile", "-", "app:app"]
