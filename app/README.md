# Streamlitin käyttöönotto

#### Streamlit-sovellus datan visuaalisointiin, analysointiin, siirtämiseen ja tutkimiseen.

## Buildaa Docker-kontit
1. Rakenna kaikki tarvittavat Docker-kontit komennolla:
```
bash docker compose --build
```

2. Nosta kaikki kolme konttia pystyyn (Database, Ingestion, App)
```
docker compose up
```

3. Sovellus on nyt käytettävissä selaimessa:
- http://localhost:8501

4. Lopuksi pysäytä kontit:
```
# Ensin
Ctrl + C
# Edellisen jälkeen
docker compose down
```