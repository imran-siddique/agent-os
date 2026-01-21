# Dockerfile for Cross-Model Verification Kernel Sandbox
# This provides an isolated environment for running generated code

FROM python:3.11-slim

# Set working directory
WORKDIR /sandbox

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd -m -u 1000 sandboxuser && \
    chown -R sandboxuser:sandboxuser /sandbox

USER sandboxuser

# Set resource limits
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command
CMD ["python3"]
