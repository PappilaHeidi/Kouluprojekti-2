# PROJEKTIOPINNOT 2: Koneoppiminen (2024) - Mojovat 

##### Projektin tekijät ovat:

* Andreas Konga
* Joni Kauppinen
* Linnea Kauppinen
* Heidi Pappila
* Ville Mörsäri

## Projektin kuvaus

Tässä projektissa pyritään tarjoamaan Kainuun Hyvinvointialueelle data-analyysipalveluja, jotka tukevat päätöksentekoa ja parantavat palveluiden laatua. Analyysit keskittyvät erityisesti henkilöstön työtyytyväisyyteen (NES) ja asiakastyytyväisyyteen (HOPP), keskittyen tärkeimpiin osa-alueisiin, kuten johtamiseen, sitoutuneisuuteen ja asiakaspalvelun laatuun. Tavoitteena on tuottaa hyödyllistä tietoa, joka auttaa Kainuun Hyvinvointialuetta parantamaan toimintansa tehokkuutta, kehittämään henkilöstön hyvinvointia ja asiakastyytyväisyyttä sekä optimoimaan resurssien käyttöä alueen sosiaali- ja terveyspalveluissa sekä pelastustoimessa. Data-analyysit tarjoavat selkeitä ja käytännöllisiä näkökulmia, jotka tukevat strategisten päätösten tekemistä ja palveluiden kehittämistä Kainuun alueella.

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

## Sovelluksen työkalut

##### Listattu vaaditut työkalut sovelluksen käyttöön.

* Python
* Pip
* Git
* Docker
* Docker Compose
* Streamlit

## Riippuvuksien ja työkalujen asennus ja käyttöönotto

##### Ohjeet projektin riippuvuuksien asentamiseen sekä Docker, Docker Compose ja Streamlit käyttöön.

### Riippuvuuksien asentaminen

1. **Asenna python virtuaali ympäristö komennolla:** 
```
pip install virtualenv
```
2. **Luo uusi virtuaaliympäristö komenolla:**
```
python -m venv .venv
```
3. **Aktivoi virtuaaliympäristö komennolla:**
```
# Windows:
.venv/Scripts/activate

# macOS/Linus:
source .venv/bin/activate
```
4. Vaihtoehto 1: **Asenna riippuvuudet käyttämällä komentoa:**
```
pip install -r requirements.txt
```
4. Vaihtoehto 2: **Asenna riippuvuudet käyttämällä docker composea (ohjeet alla)**

### Docker Compose

**Sisältää levykuvat ingestionille, tietokannalle ja Streamlitille**

1. **Rakenna levykuva ja kontti:**
```
docker-compose build
```
2. **Docker -kontin käynnistys:**
```
docker-compose up
```
3. **Dockerin alasajo:**
```
ctrl + c / docker-compose down
```

### CosmosDB (tietokanta) käyttöohje
**Kun Docker Compose käynnistetty**

1. **Navigoi selaimessa osoitteeseen:**

* http://localhost:8081

### Ingestion käyttöohje
**Kun Docker Compose käynnistetty**

1. **Navigoi selaimessa osoitteeseen:**

* http://localhost:8080

### Streamlit käyttöohje
**Kun Docker Compose käynnistetty**

1. **Navigoi selaimessa osoitteeseen:**

* http://localhost:8501


## Dokumentointityökalu

##### Projekti on dokumentoitu Markdown -pohjaisen MKDocs -työkalun avulla.

### MKDocs käyttöohje

1. **Navigoi oikeaan kansioon:**
```
cd diary
```

2. **Käynnistä Docker komennolla:**
```
docker compose -f docker-compose-docs.yml up
```
3. **Navigoi selaimessa osoitteeseen:**

* http://localhost:8000

4. **Dockerin alasajo:**
```
docker compose -f docker-compose-docs.yml down
```

## CosmosDB käyttöohje?

## Jotain tänne datan käsittelystä ja tietokannasta?

