FROM python:3.11-slim

# Create non-root user with home directory for security
RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
RUN chown -R appuser:appuser /app

# Ensure appuser can write to Streamlit config directory
RUN mkdir -p /home/appuser/.streamlit && \
    chown -R appuser:appuser /home/appuser/.streamlit && \
    chmod -R 755 /home/appuser/.streamlit

# Switch to non-root user
USER appuser

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]