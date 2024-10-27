# Use Python as the base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY ./shared/requirements/ingestion.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY ./ingestion/src /app/src
COPY ./shared/.env/ /app/.env

# Set environment variables for CosmosDB (optional if using env_file in docker-compose)
ENV PYTHONPATH=/app/src

# Set entrypoint
# CMD ["python", "/app/src/main.py"]
