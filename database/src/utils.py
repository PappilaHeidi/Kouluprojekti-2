from dotenv import load_dotenv
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import azure.cosmos.partition_key as PK
import os


def upsert_data(con, data):
    """Upload data to the CosmosDB container."""
    for item in data:
        try:
            con.upsert_item(item)
            print(f"Uploaded item: {item}")
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error uploading item: {e}")

    