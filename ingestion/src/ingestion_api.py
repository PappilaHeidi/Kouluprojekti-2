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
      # test which partition to use for bronze ingest
    if itool.test_partition(file.filename):
        pk = 'hopp'
    elif itool.test_partition(file.filename) is False:
        pk = 'nes'
    else:
        raise Exception('input error: file not recognized')

    # save file that was uploaded from streamlit
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    if pk == 'hopp':
        # read excel file to df
        itool.read_excel(file_path)

    if pk == 'nes':
        itool.read_excel(file_path)
        print(itool.df_from_excel)

    # process the file
    itool.column_clean_up(itool.df_from_excel)

    # save file in json format locally
    itool.json_to_file(file.filename)

    try:
        database_response = requests.post(f"http://database:8081/upload_bronze/{pk}", json={"data": itool.json_data})

        if database_response.status_code == 200:
            return {"message": "Data ingestion completed successfully."}
        else:
            return {"message": "Error during database ingestion!", "details": database_response.text}
    except requests.exceptions.RequestException as e:
        return {"message": "Failed to connect to the database service.", "details": str(e)}

