# 1. Base Layer: Use a stable, lightweight Python environment
FROM python:3.11-slim

# 2. System Optimization: Prevent Python from writing .pyc files and buffer streams
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Workspace Setup: Establish the primary system directory inside the container
WORKDIR /app

# 4. Dependency Isolation: Install system utilities needed for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Dependency Ingestion: Copy only the requirement manifest first to leverage caching
COPY requirements.txt .

# 6. Installation: Install dependencies into the container isolation bubble
RUN pip install --no-cache-dir --upgrade pip && \
    pip uninstall jwt pyjwt -y && \
    pip install --no-cache-dir -r requirements.txt

# 7. Code Mapping: Copy the rest of the application files into the working directory
COPY . .

# 8. Port Exposure: Open port 8000 for network communication
EXPOSE 8000

# 9. Runtime Execution: Launch Uvicorn, binding it to all interfaces on port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]