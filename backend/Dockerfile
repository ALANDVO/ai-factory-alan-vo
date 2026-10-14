# Backend Dockerfile - Multi-stage build for ai-factory API
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.12-slim AS runtime

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser ../factory.py ../factory.py
COPY --chown=appuser:appuser ../apps.py ../apps.py
COPY --chown=appuser:appuser ../gen.py ../gen.py
COPY --chown=appuser:appuser ../appdefs.py ../appdefs.py
COPY --chown=appuser:appuser ../appdefs_batch2.py ../appdefs_batch2.py
COPY --chown=appuser:appuser ../appdefs_batch3.py ../appdefs_batch3.py
COPY --chown=appuser:appuser ../appdefs_cloud.py ../appdefs_cloud.py
COPY --chown=appuser:appuser ../appdefs_enterprise.py ../appdefs_enterprise.py
COPY --chown=appuser:appuser ../VERSION ../VERSION

# Create necessary directories
RUN mkdir -p /home/appuser/ai-factory/repos \
    && chown -R appuser:appuser /home/appuser/ai-factory

# Switch to non-root user
USER appuser

# Add local packages to PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"
ENV PYTHONPATH="/app:/app/app"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/api/v1/health', timeout=5)" || exit 1

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]