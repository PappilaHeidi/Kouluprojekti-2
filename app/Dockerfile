# Use Python as the base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY ./shared/requirements/app.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY ./app/src /app/src
COPY ./data/ /app/data/

# Set the PYTHONPATH to make `src` available for imports
ENV PYTHONPATH=/app/src


# Set entrypoint for Streamlit
CMD ["streamlit", "run", "/app/src/main_page.py", "--server.port=8501", "--server.address=0.0.0.0"]

