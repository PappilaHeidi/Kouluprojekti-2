import streamlit as st
import requests
import pandas as pd
import joblib
from io import BytesIO
import base64
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam
import time
import utils
from models import MojovaTool as MT

st.set_page_config(
    page_title= "Työkalu",
    page_icon= "🛠️",
    layout= "wide"
)

st.logo("https://kamk.fi/wp-content/uploads/2024/05/K-logo_rgb_150dpi10686.png", size="large")

st.title("🛠️ HOPP Ennustustyökalu")
st.markdown("""
            Tältä sivulta löytyy **HOPP**-datan ennustustyökalu, joka hyödyntää koneoppimismalleja asiakastyytyväisyyden analysointiin ja ennustamiseen.
            
            Valitse käytettävä malli, tarkastele kysymyskohtaisia tuloksia ja vertaile kansallisia tuloksia.
""")

st.image("/app/src/images/ai_bg.png")
endpoint_model_hopp = "http://database:8081/get/model/CNN"
endpoint_df_hopp = "http://database:8081/get/model/dataframe"

if "radio" not in st.session_state:
    st.session_state.radio = "visible"
    st.session_state.disabled = False
    st.session_state.horizontal = False

if 'button' not in st.session_state:
    st.session_state.button = False

# myös dataframen haku mallille
@st.cache_resource
def get_model(endpoint, method):
    response = requests.get(endpoint)
    if response.status_code == 200:
        data = response.json()
        if method =='CNN':
            return handle_response(data)
        elif method == 'dataframe':
            return pd.DataFrame(data)
    else:
        st.error(f"Error: {response.status_code}, {response.text}")

def handle_response(data: str):
    # Handle the response
    str_data = (data[0]['serialized_model'])
    model_bytes = base64.b64decode(str_data)
    file_like_object = BytesIO(model_bytes)
    return joblib.load(file_like_object)



with st.spinner("Ladataan mallia ja haetaan kyselytuloksia..."):

    df = get_model(endpoint_df_hopp, 'dataframe')
    model = get_model(endpoint_model_hopp, 'CNN')
    df = utils.df_drop_columns(df)
    lagged_columns = [col for col in df.columns if 'lag1' in col]
    target_columns = [col for col in df.columns if 'lag1' not in col]
    target_column = '2_hoitajat_ja_laakarit_toimivat_hyvin_yhdessa_hoitooni_liittyvissa_asioissa'

# Radio BUTTON
chosen_model = st.radio(
    "Valitse käytettävä malli",
    ["Random Forest", "CNN", "Vertailu"],
    captions=[
        "Yksinkertainen ennustus",
        "Syväoppimismalli usealle muuttujalle",
        "Vertaile kansallisia tuloksia"
        ],
    index=None,
    label_visibility=st.session_state.radio

    )

if chosen_model == "Random Forest":
    st.markdown("# Random Forest")
    st.write("Yhden kysymysmuuttujan ennustus")
    targ_col = st.selectbox(
    "Valitse ennustettava kysymys",
    (target_columns[2:-6]),
    placeholder="Valitse yksi",
    )
    st.write("Ennustetaan muuttujan", targ_col, "arvoa")
    rf_model = MT()
    pred = rf_model.randomforest(df=df, lagged_columns=lagged_columns, target_column=targ_col)
    rf_model.plot_results()
    st.write(f"Seuraavan kauden tyytyväisyysennustus: {pred:.3f}")

elif chosen_model == "CNN":
    cnn_model = MT()
    st.write("Näytä ennustukset kysymyskohtaisesti")
    cnn_columns = st.multiselect(
    "Kysymykset",
    target_columns[2:-6],
    )
    number = st.number_input("Syötä ennustettavien jaksojen määrä", value=2)
    st.write("Ennustetaan", number, "jaksoa")
    budg_input = st.number_input("Syötä vuosibudjetti", value=25600)
    workf_input = st.number_input("Syötä vuosibudjetti", value=129745)
    st.write("Valittujen kysymysten määrä:", len(cnn_columns), "kpl")
    st.caption("Malli on opetettu datalla päivämäärään 1.9.2023 saakka.")
    result = cnn_model.cnn(model=model, cnn_columns=cnn_columns, lagged_features=df, lagged_columns=lagged_columns, steps=int(number), new_budget=budg_input, new_workforce=workf_input)
    results = cnn_model.plot_cnn_results()
    
    expander = st.expander("Lisätietoja")
    expander.write('''
        Yksidimensionaalinen konvoluutioverkko käsittelee vektorijonoa esim. sanoja tai lukuja, ikään kuin se olisi kuva. Konvoluutiosuodin liikkuu jonoa pitkin yhden ulottuvuuden mukaisesti, ja se oppii kaavoja tai lyhyitä alijaksoja. Mallia käytettiin projektissa annettuun aikajaksotettuun kyselydataan ja seuraavien jaksojen ennustamiseen.

        CNN-mallilla saavutettiin paremmat tulokset klassiseen päätöspuu-algoritmiin verrattuna. Mallit testattiin takaisintestausmenetelmällä (Backtesting), jossa RMSE-arvo otettiin jokaisen laajenevan ikkunoinnin (expanding window) iteroinnilla. 

        Testi- ja ennustusarvojen konvergoitumista oli havaittavissa, vaikka aikajaksotettu datajoukko oli vain yhdeksän havaintoa (observation) pitkä, josta vähennettin vielä yksi rivi lag-arvoa varten.
        ''')
    expander.image("/app/src/images/konv.png")

elif chosen_model == "Vertailu":
    st.write("Valitse kysymys")
    options = st.multiselect(
    "Kysymykset",
    target_columns[2:-6],
    )
    st.write("Valittujen kysymysten määrä:", len(options), "kpl")
    compare = MT()
    compare.plot_all_lines(*utils.transform_silver_hopp_for_analytics(), columns=options)
  


        