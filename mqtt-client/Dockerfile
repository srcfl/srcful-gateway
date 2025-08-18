# MQTT Client Container for Srcful Gateway
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY mqtt_service.py .

# Create non-root user for security
RUN groupadd -r mqttuser && useradd -r -g mqttuser mqttuser
RUN chown -R mqttuser:mqttuser /app

# Switch to non-root user
USER mqttuser

# Health check - check HTTP API health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8090/health', timeout=5)" || exit 1

# Expose HTTP API port
EXPOSE 8090

# Run the simple MQTT service
CMD ["python", "mqtt_service.py"]