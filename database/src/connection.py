from dotenv import load_dotenv
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import azure.cosmos.partition_key as PK
import azure.cosmos.exceptions
import os


class MojovaDB():
    def __init__(self, container):
        self.container = container
        load_dotenv('../../shared/.env')
        URL = os.getenv('COSMOSDB_ENDPOINT')  
        MASTER_KEY = os.getenv('COSMOSDB_KEY')
        self.client = cosmos_client.CosmosClient(URL, {'masterKey': MASTER_KEY}, user_agent="db_py_client", user_agent_overwrite=True)
        self.database_name = 'MojovaDB'

    def connection(self):
        database = self.client.get_database_client(self.database_name)
        return database.get_container_client(self.container)
    
    def upsert_data(self, data):
        """Upload data to the CosmosDB container."""
        for item in data:
            try:
                self.container.upsert_item(item)
                print(f"Uploaded item: {item}")
            except exceptions.CosmosHttpResponseError as e:
                print(f"Error uploading item: {e}")


