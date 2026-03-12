FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory (ingestion runs at startup, not build time)
RUN mkdir -p data

# Expose port (HuggingFace uses 7860, Render uses PORT env var)
EXPOSE 7860

# Run ingestion first (only if index missing), then start the app
CMD ["sh", "-c", "[ ! -f data/faiss_index.bin ] && python ingest.py; uvicorn app.main:app --host 0.0.0.0 --port 7860"]