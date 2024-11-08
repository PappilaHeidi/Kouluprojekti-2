
# Ingestion Tool



## Datan lataus tietokantaan
Käyttäjille tarkoitetussa Streamlit-webalustalla ladataan excel-tiedostoja. Tiedostot käsitellään ingestion-työkalulla, josta käsitelty data siirtyy bronze-tason tietokantaan.

## Miten ingestion tool käsittelee NES ja HOPSS dataa

1. Tarkistaa tiedoston nimestä RE:llä löytyykö mainintaa HOPPS:stä tai NE:stä
2. Riippuen löytyykö tiedoston nimestä HOPPS tai NES, se tekee seuraavat asiat:
    * HOPPS datasta otetaan ensimmäinen sheet käsittelyyn sillä siinä on kyselytulokset taulukkomuodossa ensimmäisissä sheeteissä
    * NES datan taulukot eivät ole järjestyksessä, joten etsitään niistä etsitään hyödyllinen kyselydata sheetin nimen perusteella, näihin sisältyy "Matriisi, "Data" ja "Kaikki vastaajat".
    * NES data muutetaan Python dict tyypiksi, eikä dataframeksi. Vain em. sheetit säästetään ja muutetaan nykyinen dict tyyppi dataframeksi.
3. Standardoi sarakenimet
3. Tallentaa datan JSON muotoon
4. Tekee post-operaation database-konttiin, josta se viedään edelleen tietokannan "Analytics" kontin bronze-osioon.

## Mitä käy kun eri dataa sekoittaa tietokannan samaan konttiin?

Uudet kentät lisätään. Jos päivitettävässä uudessa kohteessa on kenttiä, joita ei ole olemassa olevissa itemeissä, kyseiset kentät lisätään päivitettyyn itemiin vaikuttamatta aiemmin luotuihin itemeihin. CosmosDB on rakenteesta riippumaton, joten se pystyy käsittelemään eri kenttiä sisältäviä itemeitä samassa containerissa.

## Miten bronze dataa voi kysellä?
Yhdistä tietokanta-clientin avulla Analytics-konttiin:
```
SELECT * FROM c
```

## Miten bronze-datan eri entiteettejä voi kysellä

Tämä tehdään pääosin projektin tietokannan malleissa. Voit kuitenkin muokata kyselyjä tarpeittesi mukaan, esim. jos haluat hakea dataa per kvartaali ja vuosi:
```
SELECT * FROM c WHERE c.Q = 3 and c.Year=2023
```
tai medallion-tason mukaan:
```
SELECT * FROM c WHERE c.medallion = 'GOLD'
```