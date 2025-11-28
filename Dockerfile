FROM selenium/standalone-chrome:latest

# Switch to root so pip can install system-wide
USER root

WORKDIR /app

# Copy and install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend code
COPY backend /app/backend

# Set Python path
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Expose FastAPI port
EXPOSE 8000

# Switch back to seluser (required for Chrome/Selenium)
USER seluser

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
