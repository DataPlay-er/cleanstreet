# Dockerfile — Auth service
# Phase 6 will refine this with multi-stage build and non-root user.
# For now, this gets the service running in Docker Compose.

FROM python:3.12-slim

# Don't write .pyc files, and run Python unbuffered (logs appear immediately)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (better layer caching — only re-runs if requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run as a non-root user (Phase 6 will create a proper user — for now use nobody)
USER nobody

EXPOSE 8001

# Run with uvicorn. --host 0.0.0.0 required inside Docker.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]