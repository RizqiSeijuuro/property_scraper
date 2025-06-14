# Use official Python image
FROM python:3.11-slim

# Install uv (package manager) first
RUN pip install uv

# Set workdir
WORKDIR /app

# Copy project files
COPY . .

# Expose FastAPI port
EXPOSE 8080

# Run FastAPI with uvicorn
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
