import streamlit as st
import requests

# Set the Streamlit app title
st.title("Data Ingestion to CosmosDB")

# File uploader widget
uploaded_file = st.file_uploader("Upload your XLSX file", type=["xlsx"])

if uploaded_file is not None:
    # Save the uploaded file to the ingestion container
    save_path = f"/data/{uploaded_file.name}"
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

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
        response = requests.post("http://ingestion:8000/ingest/", files={"file": uploaded_file})

        if response.status_code == 200:
            st.write(response.json()["message"])
        else:
            st.write("Error during ingestion!")
