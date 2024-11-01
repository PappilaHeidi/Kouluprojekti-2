from dotenv import load_dotenv
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import azure.cosmos.exceptions
import os
import logging
from pathlib import Path
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MojovaDB():
    def __init__(self, container):
        try:
            self.container_name = container
            
            # Get the correct path to .env file
            current_dir = Path(__file__).resolve().parent
            project_root = current_dir.parent.parent
            env_path = project_root / 'shared' / '.env'
            
            logger.info(f"Looking for .env file at: {env_path}")
            
            # Load environment variables
            load_dotenv(env_path)
            
            # Get and validate environment variables
            URL = os.getenv('COSMOSDB_ENDPOINT')
            MASTER_KEY = os.getenv('COSMOSDB_KEY')
            
            if not URL or not MASTER_KEY:
                raise ValueError("Missing required environment variables: COSMOSDB_ENDPOINT or COSMOSDB_KEY")
                
            logger.info(f"Initializing Cosmos DB client with endpoint: {URL}")
            
            self.client = cosmos_client.CosmosClient(
                URL, 
                {'masterKey': MASTER_KEY},
                user_agent="mojovadb_py_client",
                user_agent_overwrite=True
            )
            self.database_name = 'MojovaDB'
            
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}", exc_info=True)
            raise

    def connect(self):
        try:

            logger.info(f"Connecting to database: {self.database_name}")
            # Create database if it doesn't exist
            self.database = self.client.create_database_if_not_exists(
                id=self.database_name
            )
            
            logger.info(f"Creating/connecting to container: {self.container_name}")
            # Create container if it doesn't exist
            self.container = self.database.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path='/medallion'),
                offer_throughput=400
            )
            
            logger.info("Successfully connected to database and container")
            
        except Exception as e:
            logger.error(f"Connection failed: {str(e)}", exc_info=True)
            raise

    def query(self, query_template):
        try:

            logger.info(f"Executing query: {query_template}")
            
            data = self.container.query_items(
                query=query_template,
                enable_cross_partition_query=True
            )
            
            result = [item for item in data]
            logger.info(f"Query returned {len(result)} items")
            
            return result
            
        except Exception as e:
            logger.error(f"Query failed: {str(e)}", exc_info=True)
            raise

    def upsert_data(self, data):
        """Upload data to the CosmosDB container"""
        try:
                
            logger.info(f"Starting upsert operation to container: {self.container_name}")
            # TODO: Could this be made better? idk
            # CosmosdB oma suositus tehdä näin. 
            for item in data:
                # Loop every item and add them seperately, this is pretty slow
                try:
                    # Add ID if its missing
                    item.setdefault("id", str(uuid.uuid4()))
                    self.container.upsert_item(item)
                except Exception as item_error:
                    logger.error(f"Failed to upsert item: {item.get('id', 'unknown')}: {str(item_error)}")
                    raise
            
            logger.info(f"Successfully upserted {len(data)} items to {self.container_name}")
            
        except Exception as e:
            logger.error(f"Upsert operation failed: {str(e)}", exc_info=True)
            raise