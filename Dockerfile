# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy model files and inference code
COPY models/ ./models/
COPY serve.py .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port for serving (SAP AI Core expects port 9001)
EXPOSE 9001

# Set environment variables
ENV MODEL_PATH=/app/models
ENV PORT=9001
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:9001/health')" || exit 1

# Run the inference server using gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:9001", "--workers", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "serve:app"]
