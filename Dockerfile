# Use python:3.11-slim as base image
FROM python:3.11-slim

# Set working directory to /app
WORKDIR /app

# Copy requirements.txt and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose port 8080
EXPOSE 8080

# Run app.py
CMD ["python", "app.py"]
