from fastapi import FastAPI, UploadFile, File
import os
import requests
import pandas as pd

app = FastAPI()

# Directory to save uploaded files
UPLOAD_DIR = "/data"  # This should match your volume mapping in Docker Compose

@app.post("/ingest/")
async def ingest(file: UploadFile = File(...)):
    # Ensure the upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Save the uploaded file to a temporary location
    temp_file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(temp_file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Load data from the CSV file into a DataFrame
    try:
        df = pd.read_excel(temp_file_path)
    except Exception as e:
        return {"message": f"Error reading excel file: {str(e)}"}

    # Convert the DataFrame to a dictionary format for the database API
    data = df.to_dict(orient='records')

    # Send the data to the database container
    try:
        database_response = requests.post("http://database:8000/ingest/", json={"data": data})

        if database_response.status_code == 200:
            return {"message": "Data ingestion completed successfully."}
        else:
            return {"message": "Error during database ingestion!", "details": database_response.text}
    except requests.exceptions.RequestException as e:
        return {"message": "Failed to connect to the database service.", "details": str(e)}

