from fastapi import FastAPI, UploadFile, File
import os
import requests
import pandas as pd
from utils import IngestionTool

app = FastAPI()

itool = IngestionTool()
# Directory to save uploaded files
UPLOAD_DIR = "./data/ingestion/"  

@app.post("/ingest/")
async def ingest(file: UploadFile = File(...)):
    # Ensure the upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # save file that was uploaded from streamlit
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # read excel file to df
    itool.read_excel(file_path)

    # process the file
    itool.column_clean_up(itool.df_from_excel)

    # Convert the DataFrame to a dictionary format for the database API
    #data = itool.df.to_dict(orient='records')

    itool.json_to_file(file.filename)

   # Send the data to the database container
   #try:
   #    database_response = requests.post("http://database:8081/ingest/", json={"data": data})

   #    if database_response.status_code == 200:
   #        return {"message": "Data ingestion completed successfully."}
   #    else:
   #        return {"message": "Error during database ingestion!", "details": database_response.text}
   #except requests.exceptions.RequestException as e:
   #    return {"message": "Failed to connect to the database service.", "details": str(e)}

