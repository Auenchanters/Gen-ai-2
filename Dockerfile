# syntax=docker/dockerfile:1

# --- Stage 1: build the React frontend ---
FROM node:20-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# --- Stage 2: Python runtime serving API + built frontend ---
FROM python:3.11-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080
WORKDIR /app

# Install the project and its cloud extra (BigQuery + Vertex/Gemini).
COPY pyproject.toml README.md ./
COPY pipeline ./pipeline
COPY server ./server
RUN pip install --no-cache-dir ".[cloud]"

# Serve the built SPA from the same origin as the API.
COPY --from=web /web/dist ./web/dist

# Run as a non-root user.
RUN useradd --create-home appuser
USER appuser

EXPOSE 8080
CMD ["sh", "-c", "uvicorn server.main:app --host 0.0.0.0 --port ${PORT}"]
