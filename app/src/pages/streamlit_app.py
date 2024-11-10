import streamlit as st
import pandas as pd
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

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        with st.form(key='query_form'):
            raw_code = st.text_area("Kirjoita SQL Tähän")
            submit_code = st.form_submit_button("Suorita")
    
    with col2:
        if submit_code:
            st.info("SQL Kysely Suoritettu")
            with st.expander("Tulokset"):
                st.write("Tulokset")