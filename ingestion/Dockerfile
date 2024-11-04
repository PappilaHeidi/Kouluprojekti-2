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
COPY ./data/ /app/data

# Set environment variables for CosmosDB (optional if using env_file in docker-compose)
ENV PYTHONPATH=/app/src

EXPOSE 8080

# Set entrypoint
#CMD ["python", "/app/src/ingestion.py"]
CMD ["uvicorn", "ingestion_api:app", "--host", "0.0.0.0", "--port", "8080"]
