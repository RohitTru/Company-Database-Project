# Base image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Cloudflared
RUN curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared && \
    chmod +x /usr/local/bin/cloudflared

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies with debug
COPY requirements.txt /app/requirements.txt
RUN pip list && pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt && pip list

# Copy application files
COPY app.py /app/app.py
COPY templates/ /app/templates/
COPY static/ /app/static/

# Expose the ports: Flask (5000) and Cloudflared tunnel (9210)
EXPOSE 5000 9210

# Start Cloudflared tunnel and Flask application
CMD ["/bin/bash", "-c", "cloudflared access tcp --hostname mysql.emerginary.com --url 127.0.0.1:9210 & python /app/app.py"]
