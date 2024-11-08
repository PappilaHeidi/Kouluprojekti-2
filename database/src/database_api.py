from fastapi import FastAPI
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import azure.cosmos.partition_key as pk
import os
import utils
from connection import MojovaDB


app = FastAPI()

# Initialize the CosmosDB connection

@app.post("/upload_bronze/hopp")
async def ingest_hopp(data: dict):
   client = MojovaDB('Analytics')
   client.connection()
   print("success for hopp")

@app.post("/upload_bronze/nes")
async def ingest_hopp(data: dict):
   db_client = MojovaDB('Analytics')
   con = db_client.connection()
   print("success for nes")