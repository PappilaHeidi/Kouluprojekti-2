



def upload_ingestion_file(uploaded_file):
    # Save the uploaded file to the ingestion container
    save_path = f"./data/ingestion/{uploaded_file.name}"
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
