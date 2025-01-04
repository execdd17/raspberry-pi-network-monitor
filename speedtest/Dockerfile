# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the speedtest script
COPY speedtest.py /app/speedtest.py

# Set working directory
WORKDIR /app

# Run the speedtest script
CMD ["python", "testspeed.py"]
