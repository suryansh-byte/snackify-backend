# Dockerfile for Snackify backend
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y gcc libpq-dev build-essential --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . /app

# Create a user to run the app
RUN useradd --create-home appuser
USER appuser

ENV PORT=5000
EXPOSE 5000

# Use gunicorn for production — use shell form so $PORT is expanded at runtime
CMD sh -c "gunicorn app:app --bind 0.0.0.0:$PORT --workers 2"
