# Agent OS Development Dockerfile
# Build: docker build -t agent-os .
# Run:   docker run -it agent-os

FROM python:3.11-slim

LABEL maintainer="Imran Siddique"
LABEL description="Agent OS - A kernel architecture for governing autonomous AI agents"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./
COPY src/ ./src/
COPY modules/ ./modules/

# Install Agent OS with all optional dependencies
RUN pip install --no-cache-dir -e ".[full,dev]"

# Copy the rest of the project
COPY . .

# Create a non-root user
RUN useradd -m -s /bin/bash agentos
USER agentos

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose API port
EXPOSE 8080

# Default command - run governance API server
CMD ["python", "-m", "agent_os.server", "--host", "0.0.0.0", "--port", "8080"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:8080/health'); assert r.status_code == 200" || exit 1
