# Ingestion Tool

Buildaa docker-kontit
```
docker compose build
```
Nosta kaikki kolme konttia pystyyn (Database, Ingestion, App)
```
docker compose up
```
Avaa Streamlit selain jos haluat ladata excel-tiedostoja tai tehdä graafisia kyselyjä tietokantaan.


## Datan lataus tietokantaan
Käyttäjille tarkoitetussa Streamlit-webalustalla adminit voivat ladata excel-tiedostoja ja tehdä kyselyjä. Tiedostot käsitellään ingestion-työkalulla, josta käsitelty data siirtyy bronze-tason tietokantaan.

## Miten ingestion tool käsittelee NES ja HOPSS dataa

1. Tarkistaa tiedoston nimestä RE:llä löytyykö mainintaa HOPPS:stä tai NES:stä
2. Riippuen löytyykö tiedoston nimestä HOPPS tai NES, se tekee seuraavat asiat:
    * HOPPS datasta otetaan ensimmäinen sheet käsittelyyn sillä siinä on kyselytulokset taulukkomuodossa ensimmäisissä sheeteissä
    * NES datan taulukot eivät ole järjestyksessä, joten etsitään niistä hyödyllinen kyselydata sheetin nimen perusteella, näihin sisältyy "Matriisi, "Data" ja "Kaikki vastaajat".
    * NES data muutetaan Python dict tyypiksi, eikä dataframeksi. Vain em. sheetit säästetään ja muutetaan nykyinen dict tyyppi dataframeksi.
3. Standardoi sarakenimet
3. Tallentaa datan JSON muotoon
4. Tekee post-operaation database-konttiin, josta se viedään edelleen tietokannan "Analytics" kontin bronze-osioon.

## Mitä käy kun eri dataa sekoittaa tietokannan samaan konttiin?

Uudet kentät lisätään. Jos päivitettävässä uudessa kohteessa on kenttiä, joita ei ole olemassa olevissa itemeissä, kyseiset kentät lisätään päivitettyyn itemiin vaikuttamatta aiemmin luotuihin itemeihin. CosmosDB on rakenteesta riippumaton, joten se pystyy käsittelemään eri kenttiä sisältäviä itemeitä samassa containerissa.

## Miten tehdä suoria kyselyjä tietokantaan

Lue ohjeet ja esimerkit tietokanta (/database/README.md) hakemistosta, miten luoda yhteys jupyterillä paikallisesti ja tehdä omia kyselyjä.