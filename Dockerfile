FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create database directory if needed
RUN mkdir -p /app

# Expose ports
EXPOSE 7860
EXPOSE 7861

# Run the application (FastAPI API on 7860)
CMD ["python", "app.py"]
