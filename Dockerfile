# =============================================================================
# LeechBot - Dockerfile
# =============================================================================
# Multi-stage build for minimal image size
# Supports: x86_64, ARM64 (Oracle Cloud, Raspberry Pi, Apple Silicon)
# =============================================================================

FROM python:3.12-slim AS base

# Prevent Python from buffering output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    aria2 \
    p7zip-full \
    unrar \
    unzip \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install megatools (not in all repos)
RUN curl -fsSL https://github.com/megous/megatools/releases/download/1.11.1/megatools-1.11.1.tar.gz | tar xz \
    && cd megatools-1.11.1 && ./configure && make && make install && cd .. \
    && rm -rf megatools-1.11.1 \
    || apt-get update && apt-get install -y megatools && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p sessions downloads temp work thumbnails logs

# Set permissions
RUN chmod +x main.py 2>/dev/null || true

# Default port for web dashboard
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Run the bot
CMD ["python3", "-m", "leechbot"]
