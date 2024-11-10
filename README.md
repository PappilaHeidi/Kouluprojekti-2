









## Projektin rakenne
```
PROJECT_SIGMA/
│
├── docker-compose.yml             # Compose file to manage containers and networking
│
├── ingestion/                     # Container 1: Data ingestion
│   ├── Dockerfile                 # Dockerfile for ingestion container
|   ├──README.md
│   ├── src/                       # Source code for ingestion
│       ├── __init__.py
│       ├── ingestion_api.py       # FastAPI ingestion  
│       └── utils.py               # Utility functions for Ingestion tool
│
├── database/                      # Container 2: CosmosDB Query service
│   ├── Dockerfile                 # Dockerfile for database container
|   ├── README.md
|   ├── db_templates/              # SQL templates used for querying
|   |   ├── bronze.sql             # Bronze template
│   ├── src/                       # Source code for database query service
│   │   ├── __init__.py
│   │   ├── connection_tool.py     # Connection module to database
│   │   ├── database_api.py        # Fast API for query service
│   │   └── utils.py               # Utility functions for database api
│
├── app/                           # Container 3: Streamlit app
│   ├── Dockerfile                 # Dockerfile for Streamlit container
|   ├── README.md
│   ├── src/                       # Source code for Streamlit
│   │   ├── __init__.py
│   │   ├── streamlit_app.py       # Entrypoint for Streamlit (UI and API calls)
│   │   └── utils.py               # Utility functions for streamlit
│
└── shared/                        # Shared resources and configurations
    ├── requirements/              # Requirements files for each container
    │   ├── ingestion.txt
    │   ├── database.txt
    │   |── app.txt
    │   └── local.txt
    └── .env                       # Environment variables

```   