


## Miten bronze-datan eri entiteettejä voi kysellä notebookissa

Tämä tehdään pääosin projektin tietokannan malleissa Streamlitin kautta. Voit kuitenkin muokata kyselyjä tarpeittesi mukaan, esim. jos haluat hakea dataa per kvartaali ja vuosi notebookissa.

Yhdistä tietokantaan clientilla Analytics-konttiin:

```
#db_connect.ipynb

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import os
import json
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, PartitionKey

load_dotenv('../../shared/.env')

# database env
URL = os.getenv('COSMOSDB_ENDPOINT')  
MASTER_KEY = os.getenv('COSMOSDB_KEY')

# init client
client = cosmos_client.CosmosClient(URL, {'masterKey': MASTER_KEY}, user_agent="", user_agent_overwrite=True)

# Create a database (if it doesn't exist)
database_name = 'MojovaDB'
database = client.get_database_client(database_name)

# Create a container (if it doesn't exist)
container_name = 'Analytics'
try:
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path='/medallion'),
        offer_throughput=400
    )
except exceptions.CosmosResourceExistsError:
    container = database.get_container_client(container_name)

import pandas as pd
query = "SELECT * FROM c WHERE c['/medallion'] = 'bronze_nes'"
data = container.query_items(query=query, enable_cross_partition_query=True)

# data contains iterator object
data = [item for item in data]

df = pd.DataFrame(data)
df
```

Voit tehdä erilaisia kyselyjä, kuten:
```
query = "SELECT * FROM c WHERE c['/medallion'] = 'bronze_nes' AND c.tyoyksikko = 'ENSIHOITO'"
```
Esimerkkitulos: 

| org_id | unnamed:_1 | tyoyksikko | tyonkuva                                     | unnamed:_4 | tyosuhde                                          | koulutus | tyovuoro | tyosuhteen_pituus | uskon_org_paamaariin | ... | org_innostaa | tyoskentelen_3v_todnak | valmis_panostamaan | id                                   | /medallion  | _rid                     | _self                                         | _etag                                     | _attachments | _ts         |
|--------|------------|------------|----------------------------------------------|------------|---------------------------------------------------|----------|----------|-------------------|----------------------|-----|-------------|-------------------------|--------------------|--------------------------------------|-------------|-------------------------|-----------------------------------------------|-------------------------------------------|--------------|-------------|
| 117    | Ensihoito  | ENSIHOITO  | 16                                           | Sairaanhoitaja, audionomi, terveydenhoitaja         | 1        | 3        | 3.0               | 5                    | ... | 3           | 5                       | 5                  | f05d352f-857b-4367-aa74-afba58d78e79 | bronze_nes | 1kAqANsuEko1AAAAAAAAAA== | dbs/1kAqAA==/colls/1kAqANsuEko=/docs/1kAqANsuE... | "6f005621-0000-4700-0000-6730a7c30000" | attachments/  | 1731241923 |
| 117    | Ensihoito  | ENSIHOITO  | 20                                           | Ensihoitaja / vastaava ensihoitaja                 | 1        | 3        | 3.0               | 4                    | ... | 4           | 4                       | 5                  | e057e003-f7d3-414a-af6d-d10e82bf5849 | bronze_nes | 1kAqANsuEkpNAAAAAAAAAA== | dbs/1kAqAA==/colls/1kAqANsuEko=/docs/1kAqANsuE... | "6f006e21-0000-4700-0000-6730a7c40000" | attachments/  | 1731241924 |
| 117    | Ensihoito  | ENSIHOITO  | 20                                           | Ensihoitaja / vastaava ensihoitaja                 | 1        | 3        | 3.0               | 4                    | ... | 2           | 4                       | 4                  | d4c5e1a8-43dd-43f4-a32a-01360c7c3c14 | bronze_nes | 1kAqANsuEkpWAAAAAAAAAA== | dbs/1kAqAA==/colls/1kAqANsuEko=/docs/1kAqANsuE... | "6f007c21-0000-4700-0000-6730a7c40000" | attachments/  | 1731241924 |


## Kehitteillä
docker konttien buildin yhteydessä scripti, joka luo tietokannan kontit jos niitä ei ole olemassa.

#TODO script for db container and partitionkey init when container is served