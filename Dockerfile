FROM python:3.9-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .



# Start gunicorn
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:${PORT}:-8000", "--workers", "3", "--log-file", "-"]