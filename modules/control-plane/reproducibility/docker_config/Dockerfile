FROM python:3.10-slim-bullseye

# Set environment variables for reproducibility
ENV PYTHONHASHSEED=0
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements first for better caching
COPY reproducibility/requirements_frozen.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements_frozen.txt

# Copy the rest of the code
COPY . /workspace/

# Install the package in development mode
RUN pip install -e .

# Create results directory
RUN mkdir -p /workspace/results

# Set default command
CMD ["bash"]

# Labels
LABEL maintainer="Agent Control Plane Contributors"
LABEL version="1.1.0"
LABEL description="Reproducibility environment for Agent Control Plane experiments"
