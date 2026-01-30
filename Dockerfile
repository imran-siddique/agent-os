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

# Default command - run tests to verify installation
CMD ["python", "-c", "import agent_os; print('✅ Agent OS installed successfully!'); print(f'Version: {agent_os.__version__ if hasattr(agent_os, \"__version__\") else \"dev\"}')"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import agent_os" || exit 1
