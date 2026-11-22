# Accessible Campus Navigator - Production Dockerfile
# Multi-stage optimized build for Python 3.11 Streamlit application

FROM python:3.11-slim AS base

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    CAMPUS_ENV=production \
    CAMPUS_PORT=8501

# Create non-root user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

# Set work directory
WORKDIR /app

# Install Python dependencies first for caching layers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create required persistent and log directories and set ownership
RUN mkdir -p /app/data /app/database /app/backups /app/logs && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose Streamlit default port
EXPOSE 8501

# Container healthcheck using Python standard library
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# Start Streamlit application
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
