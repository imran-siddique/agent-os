# Agent Control Plane Docker Image
# 
# Multi-stage build for production deployment
# Based on Python 3.11 slim image

FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY pyproject.toml setup.py MANIFEST.in ./
COPY src/ ./src/
COPY README.md LICENSE ./

# Install the package
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN useradd -m -u 1000 acp && chown -R acp:acp /app
USER acp

# Copy examples and docs (optional for runtime)
COPY examples/ ./examples/
COPY docs/ ./docs/

# Expose port for potential API server
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ACP_DATA_DIR=/app/data

# Create data directory
RUN mkdir -p /app/data

# Default command (can be overridden)
CMD ["python", "-m", "agent_control_plane"]

# -------------------
# Development Stage
# -------------------
FROM base as development

# Switch back to root for dev tools installation
USER root

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest>=7.0.0 \
    pytest-cov>=4.0.0 \
    black>=23.0.0 \
    flake8>=6.0.0 \
    mypy>=1.0.0 \
    ipython \
    jupyter

# Switch back to acp user
USER acp

# Development command
CMD ["bash"]

# -------------------
# Production Stage
# -------------------
FROM base as production

# Production optimizations
ENV PYTHONOPTIMIZE=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import agent_control_plane; print('healthy')" || exit 1

# Production command
CMD ["python", "-m", "agent_control_plane"]
