from fastapi import FastAPI
from connection import CosmosDBConnection

app = FastAPI()

# Initialize the CosmosDB connection

@app.post("/upload_bronze/")
async def ingest(data: dict):
    cosmos_connection = CosmosDBConnection(container='HOPP', medallion='Bronze')
    # Call the upload method to insert data into CosmosDB
    cosmos_connection.upload_data(data['data'])
    return {"message": "Data ingestion to CosmosDB completed successfully."}
