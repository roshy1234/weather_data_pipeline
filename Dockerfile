# Use a lightweight Python 3.10 base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the pipeline code
COPY . .

# Run the worker in the foreground with unbuffered output
CMD ["python", "-u", "orchestrator.py"]