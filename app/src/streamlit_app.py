import streamlit as st
import requests
from utils import upload_ingestion_file

# Set the Streamlit app title
st.title("Data Ingestion to CosmosDB")

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
