

import requests
import numpy as np
import pandas as pd



def upload_ingestion_file(uploaded_file):
    # Save the uploaded file to the ingestion container
    save_path = f"./data/ingestion/{uploaded_file.name}"
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

def df_drop_columns(df):
    drop_columns = ['_ts', '/method', '_etag', '_attachments', '_self', 'id', '_rid']
    df = df.drop(drop_columns, axis=1)
    return df


def transform_silver_hopp_for_analytics():
    """Nasty function"""
    response = requests.get('http://database:8081/get/gold/hopp')
    data = response.json()
    df = pd.DataFrame(data)
    df['quarter'] = df['quarter'].str.replace('.0_', '_', regex=False)
    # Split the dataset into kainuu and kooste
    kainuu_df = df[df['datajoukko'] == 'kainuu']
    kooste_df = df[df['datajoukko'] == 'kooste']
    # Identify missing quarters in kainuu
    kainuu_quarters = set(kainuu_df['quarter'])
    kooste_quarters = set(kooste_df['quarter'])
    missing_quarters = list(kooste_quarters - kainuu_quarters)

    # Group "kooste" by quarter and calculate mean
    kooste_grouped = kooste_df.groupby('quarter').mean(numeric_only=True)

    # Calculate averages for common quarters
    common_quarters = list(kainuu_quarters & kooste_quarters)
    kooste_avg_common = kooste_grouped.loc[common_quarters].mean()
    kainuu_avg_common = kainuu_df[kainuu_df['quarter'].isin(common_quarters)].mean(numeric_only=True)

    # Lasketaan korjauskerroin kainuu vs kaikki
    correction = kainuu_avg_common - kooste_avg_common

    # Lisätään korjaus arvoihin. Asteikko 0-5 joten yksinkertainen lisäys toimii
    missing_kooste_averages = kooste_grouped.loc[missing_quarters]
    corrected_values = missing_kooste_averages.add(correction, axis=1)

    # max tyytyväisyys = 5
    corrected_values = corrected_values.clip(upper=5)
    # Uudet rivit kainuun datajoukolle
    new_rows = corrected_values.reset_index()
    new_rows['datajoukko'] = 'kainuu'

    # Append the corrected rows to kainuu dataset
    kainuu_df = pd.concat([kainuu_df, new_rows], ignore_index=True)

    kainuu_df = kainuu_df.fillna(method='bfill')
    drop_columns = ['_ts', '/medallion', '_etag', '_attachments', '_self', 'id', '_rid']

    kooste_df['period'] = kooste_df['quarter'].apply(lambda x: f"{x[-4:]}Q{x[:2].lstrip('0')}")
    kainuu_df['period'] = kainuu_df['quarter'].apply(lambda x: f"{x[-4:]}Q{x[:2].lstrip('0')}")
    kooste_df['period'] = pd.PeriodIndex(kooste_df['period'], freq='Q')
    kainuu_df['period'] = pd.PeriodIndex(kainuu_df['period'], freq='Q')

    kainuu_df.sort_values(by='period', inplace=True)
    kooste_df.sort_values(by='period', inplace=True)

    kainuu_df.drop(drop_columns, axis=1, inplace=True)
    kooste_df.drop(drop_columns, axis=1, inplace= True)
    return kainuu_df, kooste_df
