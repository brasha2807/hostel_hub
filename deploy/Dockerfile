# =========================================================
# HOSTEL HUB - PRODUCTION DOCKERFILE
# =========================================================

FROM python:3.12-slim

# Set environment flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false \
    STREAMLIT_SERVER_MAX_UPLOAD_SIZE=128 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# Install minimal OS dependencies for SQLite & image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create non-root system user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose Streamlit port
EXPOSE 8501

# Healthcheck to verify container health
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py"]
