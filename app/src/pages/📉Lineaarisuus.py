import streamlit as st
import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import plotly.graph_objects as go


st.set_page_config(
    page_title= "Lineaarisuus",
    page_icon= "📉",
    layout= "wide"
)

# Lisätään sovelluksen kuvaus ja käyttöohjeet
st.markdown("""
# 📊 HOPP Lineaarinen Regressioanalyysi

Tämä sovellus analysoi asiakaspalautedataa ja ennustaa tulevia trendejä lineaarisen regression avulla.

## 📝 Käyttöohjeet:
1. Valitse ensin haluamasi kysymys pudotusvalikosta
2. Valitse tarkasteltava yksikkö
3. Sovellus näyttää:
   - Historiallisen datan sinisellä viivalla
   - Ennusteen seuraavalle 5 kvartaalille punaisella katkoviivalla

## ℹ️ Tietoa analyysistä:
- Ennuste perustuu lineaariseen regressioon
- Analyysi huomioi vain täydelliset vastaukset (ei puuttuvia arvoja)
- Graafissa X-akseli näyttää vuosineljännekset ja Y-akseli keskiarvot
""")

# Asetetaan API-osoite
api_url = "http://database:8081/get/silver/hopp"

@st.cache_data
def fetch_data():
    """Hakee datan REST-API:n kautta ja käsittelee sen."""
    try:
        response = requests.get(api_url)
    except Exception as e:
        print("NOT GOOD: ", e)
        raise Exception("shutting down!!!", e)

    if response.status_code == 200:
        data = pd.DataFrame(response.json())
        # Määritä numeeriset sarakkeet (kysymykset 1-22)
        numeric_columns = [col for col in data.columns if col.split('_')[0].isdigit()]
        # Suodata vain halutut yksiköt
        selected_units = ["AIKTEHOHO", "EALAPSAIK", "ENSIHOITO"]
        data = data[data["unit_code"].isin(selected_units)]
        # Korvaa 'E' arvot NaN:lla ja muunna numerot
        data[numeric_columns] = data[numeric_columns].replace('E', pd.NA)
        data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors='coerce')
        return data, numeric_columns, selected_units
    else:
        st.error(f"Virhe haettaessa dataa: {response.status_code}")

def sort_quarters(df):
    """Järjestää vuosineljännekset oikeaan järjestykseen."""
    def quarter_to_float(q):
        quarter, year = q.split('_')
        return int(year) + (int(quarter) - 1) / 4

    df['quarter_float'] = df['quarter'].apply(quarter_to_float)
    df = df.sort_values(by='quarter_float').drop(columns='quarter_float')
    return df

def generate_future_quarters(last_quarter, num_future):
    """Luo seuraavat kvartaalit viimeisen tunnetun kvartaalin jälkeen."""
    quarter, year = map(int, last_quarter.split('_'))
    future_quarters = []
    for _ in range(num_future):
        quarter += 1
        if quarter > 4:
            quarter = 1
            year += 1
        future_quarters.append(f"{quarter}_{year}")
    return future_quarters

def calculate_averages(data, numeric_columns):
    """Laskee yksikkö- ja kansalliset keskiarvot."""
    unit_avg = data.groupby(['unit_code', 'quarter'])[numeric_columns].mean().reset_index()
    national_avg = data.groupby('quarter')[numeric_columns].mean().reset_index()
    
    unit_avg = sort_quarters(unit_avg)
    national_avg = sort_quarters(national_avg)
    
    return unit_avg, national_avg

# Hakee ja käsittelee datan
data, numeric_columns, selected_units = fetch_data()
unit_avg, national_avg = calculate_averages(data, numeric_columns)

# Lisätään ohjeistus kysymyksen valintaan
st.markdown("""
### 🔍 Kysymyksen valinta
Valitse alla olevasta valikosta kysymys, jonka trendiä haluat analysoida:
""")

# Valitse kysymys
selected_question = st.selectbox("Valitse kysymys", numeric_columns)

# Lisätään ohjeistus yksikön valintaan
st.markdown("""
### 🏥 Yksikön valinta
Valitse yksikkö, jonka dataa haluat tarkastella:
""")

# Luo lineaarisen regression visualisointi
def create_plotly_chart(data, selected_unit, selected_question):
    """Visualisoi historialliset tiedot ja ennusteet Plotlyn avulla."""
    unit_data = data[data["unit_code"] == selected_unit]
    
    avg_data = unit_data.groupby("quarter")[selected_question].mean().reset_index()
    avg_data = sort_quarters(avg_data)

    avg_data = avg_data.dropna(subset=[selected_question])

    if avg_data.shape[0] > 1:
        X = np.arange(avg_data.shape[0]).reshape(-1, 1)
        y = avg_data[selected_question]
        
        model = LinearRegression()
        model.fit(X, y)

        last_quarter = avg_data['quarter'].iloc[-1]
        future_quarters = generate_future_quarters(last_quarter, 5)
        future_X = np.arange(len(X), len(X) + len(future_quarters)).reshape(-1, 1)
        predictions = model.predict(future_X)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=avg_data['quarter'],
            y=y,
            mode='lines+markers',
            name='Historiallinen data',
            line=dict(color='blue'),
            marker=dict(size=8)
        ))

        fig.add_trace(go.Scatter(
            x=future_quarters,
            y=predictions,
            mode='lines+markers',
            name='Ennusteet',
            line=dict(color='red', dash='dash'),
            marker=dict(size=8, symbol='x')
        ))

        fig.update_layout(
            title=f"{selected_unit} - {selected_question} - Asiakaspalautteen keskiarvot",
            xaxis=dict(title="Kvartaali (vuosi)", tickangle=-45),
            yaxis=dict(title="Keskiarvo"),
            legend=dict(title="Selite"),
            template="plotly_white"
        )

        return fig
    else:
        return None

# Näytä lineaarisen regression visualisointi
selected_unit = st.selectbox("Valitse yksikkö", selected_units)

# Lisätään selite graafille
st.markdown("""
### 📈 Trendianalyysi
Alla näet valitun yksikön historiallisen datan ja ennusteen:
- **Sininen viiva**: Toteutunut historiallinen data
- **Punainen katkoviiva**: Ennuste tuleville kvartaaleille
""")

chart = create_plotly_chart(data, selected_unit, selected_question)
if chart is not None:
    st.plotly_chart(chart)
else:
    st.warning(f"Ei riittävästi dataa ennustamiseen kysymykselle {selected_question} yksikölle {selected_unit}.")

# Lisätään huomautus datan tulkinnasta
st.markdown("""
---
### ⚠️ Huomioitavaa
- Ennuste on suuntaa-antava ja perustuu historialliseen dataan
- Ennusteen luotettavuus riippuu historiallisen datan määrästä ja laadusta
- Puuttuvat arvot on poistettu analyysistä
""")