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
|   ├── README.md                  # Documentation and use-guide for Streamlit
│   ├── src/                       # Source code for Streamlit
│   │   ├── __init__.py
│   │   ├── streamlit_app.py       # Entrypoint for Streamlit (UI and API calls)
│   │   └── utils.py               # Utility functions for streamlit
│
└── shared/                        # Shared resources and configurations
    ├── requirements.txt           # Combined requests into one file
    │── requirements/              # Requirements files for each container
    │   ├── ingestion.txt
    │   ├── database.txt
    │   |── app.txt
    │   └── local.txt
    └── .env                       # Environment variables

```  

## Projektin käyttöönotto

Projektin koodeja ajetaan pääsääntöisesti Python Notebookkien avulla. Tätä varten sinun tulee asentaa tarvittavat Python-kirjastot.

### Python kirjastot
Luo virtuaaliympäristö
```bash
python3 -m venv .venv
```

Aktivoi virtuaaliympäristö
```bash
source .venv/bin/activate  ## MAC Tms
source .venv/Scripts/activate ## Win 
```
tai
```powershell
.\.venv\Scripts\Activate.ps1
```
tai
```cmd
.\.venv\Scripts\activate.bat
```

Asenna python kirjastot
```bash
python -m pip install --upgrade pip
python -m pip install -r shared/requirements.txt
```

### .env asennus

.env -tiedostoon lisätään tarvittavia muuttujia, esimerkiksi tietokanta yhteyksiä varten tarvittavat URL:it, avaimet ja salasanat voidaan lisätä
.env -tiedostoon. Siirrä .env tiedosto ./shared/ -kansioon.

### Tietokanta API:n ajo

Aktivoi ensin terminaalissa python .venv, jonk asensit aiemmin. Käynnistä sen jälkeen Tietokanta API:
```bash
python database/run_api.py
```

### Tietokanta docker ajo

Alla olevan komennon avulla voit buildaa tietokanta API dockerin
```bash
docker build -t database-api -f ./database/Dockerfile .
```

Näin ajat kyseisen docker imagen
```bash
docker run -d --name database-api -p 8082:8082 database-api
```

Näin poistat
```bash
docker stop database-api
docker rm database-api
```

### Tietokanta API:n käyttö

Voit hekea esimerkiksi Bronze-tason datat. Kyselyt voit ajaa suoraan selaimesta, ainakin Chromen Pretty Print ominaisuus on ison datamäärän kanssa kätevä.
```
http://localhost:8082/get/silver/nes
```
formaatti on
```
http://localhost:8082/get/medallion/source
```

Voit ajaa Silver pipeline datat
```
http://localhost:8082/process/silver/hopp
```
Silver pipeline ajo, lataa Bronze-tason datat, ajaa sille Transformaatiot ja tallentaa tietokantaan. 
Formaatti on vastaava, kuin yllä. 

## Exit / Sulku 

Ctrl + C