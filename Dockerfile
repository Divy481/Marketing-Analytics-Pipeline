FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PostgreSQL connector
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

EXPOSE 8000

# Run ETL pipeline first and then launch REST API server
CMD python run_pipeline.py && uvicorn api.main:app --host 0.0.0.0 --port 8000
