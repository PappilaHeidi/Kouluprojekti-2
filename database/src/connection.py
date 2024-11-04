import os
from azure.cosmos import CosmosClient, exceptions

class CosmosDBConnection:
    def __init__(self, container: str = 'HOPP', medallion: str = 'Bronze'):
        # Load environment variables
        self.endpoint = os.getenv("COSMOSDB_ENDPOINT")
        self.key = os.getenv("COSMOSDB_KEY")
        self.database_name = os.getenv("COSMOSDB_DATABASE_NAME")
        if container == 'HOPP':
            match medallion:
                case 'Bronze':
                    self.container= os.getenv("CONTAINER_HOPP_BRONZE_NAME")
                case 'Silver':
                    self.container= os.getenv("CONTAINER_HOPP_SILVER_NAME")
                case 'Gold':
                    self.container= os.getenv("CONTAINER_HOPP_GOLD_NAME")
        elif container == 'NES':
            match medallion:
                case 'Bronze':
                    self.container= os.getenv("CONTAINER_NES_BRONZE_NAME")
                case 'Silver':
                    self.container= os.getenv("CONTAINER_NES_SILVER_NAME")
                case 'Gold':
                    self.container= os.getenv("CONTAINER_NES_GOLD_NAME")
        else:
            print("Wrong medallion parameter")
        
        # Initialize the CosmosDB client
        self.client = CosmosClient(self.endpoint, self.key)
        self.database = self.client.get_database_client(self.database_name)
        self.container = self.database.get_container_client(self.container)
        

    def upload_data(self, data):
        """Upload data to the CosmosDB container."""
        for item in data:
            try:
                self.container.upsert_item(item)
                print(f"Uploaded item: {item}")
            except exceptions.CosmosHttpResponseError as e:
                print(f"Error uploading item: {e}")

    def get_data(self):
        pass
