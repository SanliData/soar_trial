FROM python:3.11-slim

WORKDIR /app

***REMOVED*** Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

***REMOVED*** Copy requirements first (for better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

***REMOVED*** Copy application code
COPY src/ ./src/

***REMOVED*** Create data directory (stateless - Cloud Run uses ephemeral storage)
RUN mkdir -p /app/data && chmod 755 /app/data

***REMOVED*** Copy entrypoint script (strip CRLF so shebang works on Linux)
COPY entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//' /app/entrypoint.sh && chmod +x /app/entrypoint.sh

***REMOVED*** Environment variables
ENV PYTHONPATH=/app
ENV ENV=production
ENV FINDEROS_HOST=0.0.0.0
ENV PORT=8080

***REMOVED*** Expose port (Cloud Run uses PORT env var)
EXPOSE 8080

***REMOVED*** Run with entrypoint script (reads PORT from environment)
ENTRYPOINT ["/app/entrypoint.sh"]
