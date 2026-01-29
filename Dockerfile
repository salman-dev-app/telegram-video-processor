# Dockerfile
FROM python:3.9-slim

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# COPY ALL FILES MANUALLY to prevent corruption
COPY app.py /app/app.py
COPY config.py /app/config.py
COPY database.py /app/database.py
COPY video_processor.py /app/video_processor.py
COPY channel_uploader.py /app/channel_uploader.py
COPY auth_manager.py /app/auth_manager.py
COPY queue_manager.py /app/queue_manager.py
COPY handlers.py /app/handlers.py
COPY utils.py /app/utils.py

# Expose port (Railway requirement)
EXPOSE $PORT

# Start the application
CMD ["python", "app.py"]
