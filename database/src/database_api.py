from fastapi import FastAPI, HTTPException
from typing import List, Dict
import logging
from connection_tool import MojovaDB
from utils import MojovaModels
from pipeline_manager import PipelineManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Pipeline API")
silver_pipeline = PipelineManager('bronze', 'silver')
gold_pipeline = PipelineManager('silver', 'gold')

# What medallion layers are in use
VALID_LAYERS = ['bronze', 'silver', 'gold']
# What data sources we have
VALID_SOURCES = ['hopp', 'nes']
# Map medallion layers to database containers
CONTAINER_MAPPING = {
    'bronze': 'Analytics',
    'silver': 'Analytics',
    'gold': 'Analytics',
    'models': 'Models'
}

# Upload endpoint for uploading data to database (Used to upload Bronze data)
@app.post("/upload/{layer}/{source}")
async def upload_data(layer: str, source: str, data: List[Dict]):
    """Upload data to specified layer"""
    layer = layer.lower()
    source = source.lower()
    
    # Error handling for the API. 
    if layer not in VALID_LAYERS:
        raise HTTPException(status_code=400, detail="Invalid layer. Use 'bronze', 'silver', or 'gold'")
    if source not in VALID_SOURCES:
        raise HTTPException(status_code=400, detail="Invalid source. Use 'hopp' or 'nes'")
        
    logger.info(f"Uploading {len(data)} records to {layer} layer for {source}")
    
    try:
        # Initiate database connection
        db = MojovaDB(CONTAINER_MAPPING[layer])
        db.connect()
        db.upsert_data(data)
        return {
            "message": f"Upload successful for {source} to {layer} layer",
            "count": len(data)
        }
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Get endpoint for querying data from the database (can be used to get sample data from Bronze/Silver/Gold)
@app.get("/get/{layer}/{source}")
async def get_data(layer: str, source: str):
    """Get data from specified layer"""
    layer = layer.lower()
    source = source.lower()
    
    if layer not in VALID_LAYERS:
        raise HTTPException(status_code=400, detail="Invalid layer. Use 'bronze', 'silver', or 'gold'")
    if source not in VALID_SOURCES:
        raise HTTPException(status_code=400, detail="Invalid source. Use 'hopp' or 'nes'")
        
    logger.info(f"Retrieving {layer} data for {source}")
    
    try:
        db = MojovaDB(CONTAINER_MAPPING[layer])
        db.connect()
        model = MojovaModels()
        query = model.get_query(f'{layer}_{source}'.lower())
        logger.info(f"Executing query: {query}")
        return db.query(query) or []
    except Exception as e:
        logger.error(f"Data retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint for running data processing pipelines (Used to trigger datapipelines)
@app.get("/process/{layer}/{source}")
async def process_data(layer: str, source: str):
    """Process data for specified layer and source"""
    layer = layer.lower()
    source = source.lower()
    
    if layer != 'silver' and layer != 'gold':
        raise HTTPException(status_code=400, detail="Only silver and gold layer processing is supported")
    if source not in VALID_SOURCES:
        raise HTTPException(status_code=400, detail="Invalid source. Use 'hopp' or 'nes'")
        
    logger.info(f"Processing {source} data for {layer} layer")
    if layer == 'silver':
        return await silver_pipeline.process_data(source, layer)

    if layer == 'gold':
        return await gold_pipeline.process_data(source, layer)