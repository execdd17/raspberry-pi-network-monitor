# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install OS packages needed for nmap
RUN apt-get update && \
    apt-get install -y nmap && \
    rm -rf /var/lib/apt/lists/*

# Create the cache directory for mac_vendor_lookup
RUN mkdir -p /root/.cache

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app_with_postgres.py /app/app_with_postgres.py

# Set working directory
WORKDIR /app

# Run the speedtest script
CMD ["python", "app_with_postgres.py"]
