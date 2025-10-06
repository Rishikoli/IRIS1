# =============================================================================
# Project IRIS - Dockerfile
# Financial Forensics Analysis Platform
# =============================================================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    curl \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p /app/data/uploads \
    /app/data/reports \
    /app/data/pdfs \
    /app/logs \
    /app/models/cache

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Install Intel optimizations
RUN pip install --upgrade pip && \
    pip install intel-extension-for-pytorch==2.6.0 && \
    pip install openvino-dev

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 iris && \
    chown -R iris:iris /app

# Switch to non-root user
USER iris

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
