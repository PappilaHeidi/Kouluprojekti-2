import uvicorn
import os
import sys
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for most verbose logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
print(src_dir)
sys.path.append(str(current_dir))

if __name__ == "__main__":
    # Configure uvicorn with more verbose logging
    uvicorn_config = uvicorn.Config(
        "src.database_api:app",
        host="0.0.0.0",
        port=8082,
        reload=True,
        reload_dirs=[str(src_dir)],
        log_level="debug",  # Set Uvicorn log level to debug
        access_log=True,    # Enable access log
        use_colors=True,    # Enable colored logging
        reload_delay=0.1,
    )
    
    server = uvicorn.Server(uvicorn_config)
    server.run()