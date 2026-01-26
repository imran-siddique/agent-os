# Dockerfile for Self-Correcting Agent Kernel
#
# Multi-stage build for production deployment
# Based on official Python slim image

FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
COPY setup.py .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-asyncio jupyter streamlit

# Copy source code
COPY . .

# Expose ports
EXPOSE 8501

# Default command for development
CMD ["streamlit", "run", "dashboard.py"]

# Production stage
FROM base as production

# Copy only necessary files
COPY src/ ./src/
COPY agent_kernel/ ./agent_kernel/
COPY cli.py .

# Create non-root user
RUN useradd -m -u 1000 scak && chown -R scak:scak /app
USER scak

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
ENTRYPOINT ["python", "cli.py"]
CMD ["--help"]
