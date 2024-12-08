import streamlit as st
import pandas as pd
import sqlite3
import requests
from utils import upload_ingestion_file

st.set_page_config(
    page_title= "Data",
    page_icon= "🔍",
    layout= "wide"
)

st.title("⚙️ Data työkalut")
st.header("🛢️☁️ Datan ingestointi → CosmosDB")
st.markdown("""
            Tällä työkalulla voit ladata `XLSX-tiedostoja` ja siirtää datan `CosmosDB-tietokantaan`.

            Lataa tiedosto, jonka jälkeen voit muuntaa sen CSV-muotoon painamalla "Download CSV file" tai siirtää sen tietokantaan painamalla "Ingest Data".
""")

# File uploader widget
uploaded_file = st.file_uploader("Lataa XLSX-tiedosto", type=["xlsx"])

if uploaded_file is not None:
    #upload_ingestion_file(uploaded_file)

    # Provide a download button for the uploaded file
    st.download_button(
        label="Download CSV file",
        data=uploaded_file,
        file_name=uploaded_file.name,
        mime="text/csv"
    )
    st.warning("HUOM! INGESTOINTI LATAA DATAN ANALYTICS PILVEEN JOKA VAIKUTTAA ANALYTIIKKAAN")

    if st.button("Ingest Data"):
        # Trigger the ingestion process via the API in the ingestion container
        st.write("Ingesting data...")
        response = requests.post("http://ingestion:8080/ingest/", files={"file": uploaded_file})

        if response.status_code == 200:
            st.write(response.status_code)
        else:
            st.write("Error during ingestion: {response.status_code} {response.text}")

# FastAPI endpoint URL for bronze hopp
endpoint_bronze_hopp = "http://database:8081/get/bronze/hopp"
endpoint_bronze_nes = "http://database:8081/get/bronze/nes"
endpoint_silver_hopp = "http://database:8081/get/silver/hopp"
endpoint_silver_nes = "http://database:8081/get/silver/nes"
endpoint_gold_hopp = "http://database:8081/get/gold/hopp"
endpoint_gold_nes = "http://database:8081/get/gold/nes"

# Funktio hakee datan apista
def fetch_data(endpoint, dataset_name):
    response = requests.get(endpoint)
    if response.status_code == 200:
        json_data = response.json()
        data = pd.DataFrame(json_data)
        st.dataframe(data, height=1000)
        return data
    else:
        st.error(f"Error: {dataset_name}, {response.text}")
        return None

st.header("🖥️💡 Hae Dataa Tietokannasta")
st.markdown("""
            Tällä työkalulla voit tarkastella tietokannasta löytyviä eri tasojen tauluja.

            Tietokannasta löytyy pronssi-, hopea- ja kultatason tauluja, jotka tarjoavat erilaisia tietosisältöjä ja analyysimahdollisuuksia.""")

col1, col2, col3 = st.columns(3)
with col1:
    st.header("🥉 Pronssitaso")
    st.write("Valitse HOPP tai NES")
    # Streamlit button
    if st.button("Fetch Bronze HOPP Data"):
        fetch_data(endpoint_bronze_hopp, "Bronze HOPP")

    if st.button("Fetch Bronze NES Data"):
        fetch_data(endpoint_bronze_nes, "Bronze NES")

with col2:
    st.header("🥈 Hopeataso")
    st.write("Valitse HOPP tai NES")
    if st.button("Fetch Silver HOPP Data"):
        fetch_data(endpoint_silver_hopp, "Silver HOPP")

    if st.button("Fetch Silver NES Data"):
        fetch_data(endpoint_silver_nes, "Silver NES")

with col3:
    st.header("🥇 Kultataso")
    st.write("Valitse HOPP tai NES")
    if st.button("Fetch Gold HOPP Data"):
        fetch_data(endpoint_gold_hopp, "Gold HOPP")
    if st.button("Fetch Gold NES Data"):
        fetch_data(endpoint_bronze_nes, "Gold NES")

st.header("🔍 SQL Kyselyjä")
st.markdown("""
            Tällä työkalulla voit suorittaa erilaisia SQL-kyselyitä tietokantaan.

            Kyselyt suoritetaan Silver-tason datalle.
""")

# Valitse Datasetti
dataset_option = st.radio("Valitse datasetti", ['💊 HOPP', '🩺 NES'])

# Funktio hakemaan datat, erona ylempään, että ei näytä/luo suoraan dataframe
def fetch_data_for_sql(endpoint, dataset_name):
    response = requests.get(endpoint)
    if response.status_code == 200:
        json_data = response.json()
        data = pd.DataFrame(json_data)
        return data
    else:
        st.error(f"Error: {dataset_name}, {response.text}")
        return None

# Jos HOPP niin näkyy vain HOPP datasetin sarakkeet yms.
if dataset_option == "💊 HOPP":
    st.header(f"{dataset_option} Data")
    st.write("Tämä kysely suoritetaan vain HOPP datalle")
    df = fetch_data_for_sql(endpoint_silver_hopp, "HOPP")
# Jos NES niin näkyy vain NES datasetin sarakkeet yms.
elif dataset_option == "🩺 NES":
    st.header(f"{dataset_option} Data")
    st.write("Tämä kysely suoritetaan vain NES datalle")
    df = fetch_data_for_sql(endpoint_silver_nes, "NES")

if df is not None:
    # SQLITE yhteys; memory käyttää RAM, jolloin ei tarvii luoda omaa tiedostoa kannalle
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()
    # Uudelleen nimetään df -> "data"
    df.to_sql('data', conn, index=False, if_exists='replace')

# Suorittaa SQL kyselyn
def sql_executor(raw_code):
    try:
        c.execute(raw_code)
        columns = [description[0] for description in c.description] # Säilyttää sarakkeiden nimet
        data = c.fetchall() # Nappaa kaiken datan
        result_df = pd.DataFrame(data, columns=columns) # Muutetaan dataframeksi
        return result_df
    except Exception as e:
        st.error(f"SQL Suoritus Virhe: {str(e)}")
        return pd.DataFrame()

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        # Kyselyn tekstikenttä ja suoritus nappi
        with st.form(key='query_form'):
            raw_code = st.text_area("Kirjoita SQL Tähän")
            submit_code = st.form_submit_button("Suorita")
            if submit_code:
                try:
                    # INSERT, UPDATE, DELETE yms. ei toimi
                    if not raw_code.strip().lower().startswith("select"):
                        st.error("Vain SELECT-kyselyt ovat sallittuja.")
                    else:
                        st.success("Kysely suoritettu onnistuneesti!")
                except Exception as e:
                    st.error(f"Virhe suorittaessa kyselyä: {str(e)}")

    with col2:
        if submit_code:
            # Näyttää itse SQL kyselyn ja tuloksen, eli dataframen
            st.code(raw_code)
            result = sql_executor(raw_code)
            st.write(result)

# Suljetaan yhteys  
conn.close()
