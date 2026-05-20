# Build stage
FROM python:3.11-slim AS base
 
WORKDIR /app
 
# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy application source
COPY app/ ./app/
 
EXPOSE 5000
 
ENV FLASK_APP=app
ENV FLASK_ENV=production
 
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]