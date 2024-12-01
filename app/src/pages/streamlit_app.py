import streamlit as st
import pandas as pd
import sqlite3
import requests
from utils import upload_ingestion_file

st.set_page_config(
    page_title= "Ingestointi",
    page_icon= "💾",
    layout= "wide"
)

st.title("🛢️☁️ Data Ingestion to CosmosDB ☁️🛢️")

# File uploader widget
uploaded_file = st.file_uploader("Upload your XLSX file", type=["xlsx"])

if uploaded_file is not None:
    #upload_ingestion_file(uploaded_file)

    # Provide a download button for the uploaded file
    st.download_button(
        label="Download CSV file",
        data=uploaded_file,
        file_name=uploaded_file.name,
        mime="text/csv"
    )

    if st.button("Ingest Data"):
        # Trigger the ingestion process via the API in the ingestion container
        st.write("Ingesting data...")
        response = requests.post("http://ingestion:8080/ingest/", files={"file": uploaded_file})

        if response.status_code == 200:
            st.write(response.status_code)
        else:
            st.write("Error during ingestion!")

# FastAPI endpoint URL for bronze hopp
endpoint_bronze_hopp = "http://database:8081/get/bronze/hopp"
endpoint_bronze_nes = "http://database:8081/get/bronze/nes"

# Streamlit button
if st.button("Fetch Bronze Hopp Data"):
    # Make the GET request
    response = requests.get(endpoint_bronze_hopp)

    # Handle the response
    if response.status_code == 200:
        json_data = response.json()
        # Display data if the request was successful
        data = pd.DataFrame(json_data)  # Assuming the endpoint returns JSON data
        st.dataframe(data, height=1000)
    else:
        st.error(f"Error: {response.status_code}, {response.text}")

if st.button("Fetch Bronze NES Data"):
    # Make the GET request
    response = requests.get(endpoint_bronze_nes)

    # Handle the response
    if response.status_code == 200:
        json_data = response.json()
        # Display data if the request was successful
        data = pd.DataFrame(json_data)  # Assuming the endpoint returns JSON data
        st.dataframe(data, height=1000)
    else:
        st.error(f"Error: {response.status_code}, {response.text}")

st.title("🛝 SQL Leikkikenttä 🛝")

# Valitse Datasetti
dataset_option = st.radio("Valitse datasetti", ['HOPP', 'NES'])

# Jos HOPP niin näkyy vain HOPP datasetin sarakkeet yms.
if dataset_option == "HOPP":
    csv = "./notebooks/playground/hopp_example.csv"
    st.header(f"Valittu {dataset_option} Data 💉")
# Jos NES niin näkyy vain NES datasetin sarakkeet yms.
elif dataset_option == "NES":
    csv = "./notebooks/playground/nes_example.csv"
    st.header(f"Valittu {dataset_option} Data 🩺")

# Luetaan CSV:t
df = pd.read_csv(csv, sep=";")
# SQLITE yhteys; memory käyttää RAM, jolloin ei tarvii luoda omaa tiedostoa kannalle
conn = sqlite3.connect(":memory:")
c = conn.cursor()
# Uudelleen nimetään df -> "data"
df.to_sql('data', conn, index=False, if_exists='replace')

# Suorittaa SQL kyselyn
def sql_executor(raw_code):
    c.execute(raw_code)
    columns = [description[0] for description in c.description] # Säilyttää sarakkeiden nimet
    data = c.fetchall() # Nappaa kaiken datan
    result_df = pd.DataFrame(data, columns=columns) # Muutetaan dataframeksi
    return result_df

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