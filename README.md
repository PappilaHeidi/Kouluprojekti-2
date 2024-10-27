









## Projektin rakenne
```
PROJECT_SIGMA/
│
├── docker-compose.yml             # Compose file to manage containers and networking
│
├── ingestion/                     # Container 1: Data ingestion
│   ├── Dockerfile                 # Dockerfile for ingestion container
│   ├── src/                       # Source code for ingestion
│   │   ├── __init__.py
│   │   ├── ingestion.py           # FastAPI ingestion  
│   │   └── utils.py               # Utility functions if needed
│   └── data/                      # Directory for sample CSV files (for testing, if any)
│       └── ingested_dataset.csv
│
├── database/                      # Container 2: CosmosDB Query service
│   ├── Dockerfile                 # Dockerfile for database container
│   ├── src/                       # Source code for database query service
│   │   ├── __init__.py
│   │   ├── connection.py          # Connection module to database
│   │   ├── api.py                 # Fast API for query service
│   │   └── utils.py               # Utility functions if needed
│
├── app/                           # Container 3: Streamlit app
│   ├── Dockerfile                 # Dockerfile for Streamlit container
│   ├── src/                       # Source code for Streamlit
│   │   ├── __init__.py
│   │   ├── streamlit_app.py       # Entrypoint for Streamlit (UI and API calls)
│   │   └── utils.py               # Utility functions if needed
│
└── shared/                        # Shared resources and configurations
    ├── requirements/              # Requirements files for each container
    │   ├── ingestion.txt
    │   ├── database.txt
    │   └── app.txt
    └── .env                       # Environment variable

```   