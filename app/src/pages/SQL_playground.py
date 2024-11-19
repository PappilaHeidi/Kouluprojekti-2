import streamlit as st
import requests
import pandas as pd

# Päänäkymä
st.set_page_config(
    page_title="SQL",
    page_icon="▶️",
    layout="wide"
)

endpoint_bronze_hopp = "http://database:8081/get_bronze/hopp"
endpoint_bronze_nes = "http://database:8081/get_bronze/nes"

st.title("SQL -Leikkikenttä")

col1,col2 = st.columns(2)

with col1:
	with st.form(key='query_form'):
		raw_code = st.text_area("Kirjoita SQL tähän")
		submit_code = st.form_submit_button("Esitä")