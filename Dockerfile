# Stage 1: Builder
FROM python:3.13-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Create venv and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Precompute data for Turbo mode
# This ensures parquet files are generated and baked into the image
RUN python precompute.py

EXPOSE 8501

# Use python for healthcheck to avoid installing curl
HEALTHCHECK CMD python -c 'import urllib.request; import sys; sys.exit(0 if urllib.request.urlopen("http://localhost:8501/_stcore/health").getcode() == 200 else 1)'

ARG BASE_PATH="/"
ENV BASE_PATH=${BASE_PATH}

ENTRYPOINT ["sh", "-c", "exec streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.baseUrlPath=${BASE_PATH} --server.enableCORS=false --server.enableXsrfProtection=false"]