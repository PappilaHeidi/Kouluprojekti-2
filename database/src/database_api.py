from fastapi import FastAPI
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import azure.cosmos.partition_key as pk
import os
from connection_tool import MojovaDB
from utils import MojovaModels

app = FastAPI()

# Initialize the CosmosDB connection

@app.post("/upload_bronze/hopp")
async def ingest_hopp(data: list[dict]):
   db = MojovaDB('Analytics')
   db.connect()
   db.upsert_data(data)
   print("success for hopp")

@app.post("/upload_bronze/nes")
async def ingest_nes(data: list[dict]):
   db = MojovaDB('Analytics')
   db.connect()

   # same as hopps
   db.upsert_data(data)
   print("success for nes")

@app.get("/get_bronze/hopp")
async def get_hopp():
   db = MojovaDB('Analytics')
   db.connect()
   
   # get template
   model = MojovaModels()
   query = model.get_query('bronze_hopp')
   print("query template fetched", query)
   data = db.query(query)
   return data

@app.get("/get_bronze/nes")
async def get_hopp():
   db = MojovaDB('Analytics')
   db.connect()
   
   # get template
   model = MojovaModels()
   query = model.get_query('bronze_nes')
   print("query template fetched", query)
   data = db.query(query)
   return data