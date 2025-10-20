# Multi-stage build for Railway
# Use official Node image instead of alpine (more reliable on Railway)
FROM node:18 AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements-railway.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Create startup script
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'python start_railway_simple.py' >> /app/start.sh && \
    chmod +x /app/start.sh

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port (Railway will set PORT environment variable)
EXPOSE $PORT

# Run the application
CMD ["/app/start.sh"]
