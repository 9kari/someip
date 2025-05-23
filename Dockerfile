FROM python:3.11-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy script to container
COPY parse_kip_links.py .

# Install Python dependencies
RUN pip install --no-cache-dir beautifulsoup4 requests

# Set entrypoint
ENTRYPOINT ["python", "parse_kip_links.py"]
