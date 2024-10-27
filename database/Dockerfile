# Use Python 3.13 as the base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY ./shared/requirements/database.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY ./database/src /app/src

# Set the PYTHONPATH to make `src` available for imports
ENV PYTHONPATH=/app/src

# Expose the API port
EXPOSE 8000

# Start the FastAPI app using Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
