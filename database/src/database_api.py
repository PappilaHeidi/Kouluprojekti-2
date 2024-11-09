from fastapi import FastAPI
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import azure.cosmos.partition_key as pk
import os
from connection_tool import MojovaDB


app = FastAPI()

# Initialize the CosmosDB connection

@app.post("/upload_bronze/hopp")
async def ingest_hopp(data: list[dict]):
   print("test")
   db = MojovaDB('Analytics')
   db.connect()
   db.upsert_data(data)
   print("success for hopp")

@app.post("/upload_bronze/nes")
async def ingest_hopp(data: list[dict]):
   db = MojovaDB('Analytics')
   db.connect()

   # same as hopps
   # db.upsert_data(data)
   print("success for nes")