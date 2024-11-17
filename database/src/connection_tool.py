from dotenv import load_dotenv
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import azure.cosmos.partition_key as PK
import azure.cosmos.exceptions
import os


class MojovaDB():
    def __init__(self, container):
        self.container_name = container
        load_dotenv('../../shared/.env')
        URL = os.getenv('COSMOSDB_ENDPOINT')  
        MASTER_KEY = os.getenv('COSMOSDB_KEY')
        self.client = cosmos_client.CosmosClient(URL, {'masterKey': MASTER_KEY}, user_agent="mojovadb_py_client", user_agent_overwrite=True)
        self.database_name = 'MojovaDB'

    def connect(self):
        self.database = self.client.get_database_client(self.database_name)
        self.container = self.database.get_container_client(self.container_name)
    
    def upsert_data(self, data):
        """Upload data to the CosmosDB container.
        Accepted types: JSON formats that are serializable.
        Must include unique id
        """
        for index, item in enumerate(data):
            try:
                # Check if the item is a dictionary
                if isinstance(item, dict):
                    self.container.upsert_item(item)
                    print(f"Uploaded item at index {index}: {item}")
                else:
                    print(f"Skipping non-dictionary item at index {index}: {item} (type: {type(item)})")
                    
            except exceptions.CosmosHttpResponseError as e:
                print(f"Error uploading item at index {index}: {e}")

    def query(self, query_template):
        data = self.container.query_items(
        query=query_template,
        enable_cross_partition_query=True
        )
        return [item for item in data]

