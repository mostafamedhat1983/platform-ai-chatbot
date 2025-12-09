FROM python:3.11-slim

# Create non-root user with explicit UID/GID for security
RUN groupadd -r -g 1000 appuser && useradd -r -u 1000 -g 1000 appuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip>=25.3 && \
    pip install --no-cache-dir -r requirements.txt
COPY main.py .
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]