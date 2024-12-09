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
        #response.raise_for_status()

def sort_quarters(df):
    """Järjestää vuosineljännekset oikeaan järjestykseen."""
    def quarter_to_float(q):
        quarter, year = q.split('_')
        return int(year) + (int(quarter) - 1) / 4  # Kvartaali float-muotoon (esim. 1_2022 -> 2022.0)

    df['quarter_float'] = df['quarter'].apply(quarter_to_float)
    df = df.sort_values(by='quarter_float').drop(columns='quarter_float')  # Poistetaan apusarake
    return df

def generate_future_quarters(last_quarter, num_future):
    """Luo seuraavat kvartaalit viimeisen tunnetun kvartaalin jälkeen."""
    quarter, year = map(int, last_quarter.split('_'))
    future_quarters = []
    for _ in range(num_future):
        quarter += 1
        if quarter > 4:  # Siirrytään seuraavaan vuoteen
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

# Streamlit-sovelluksen UI
st.title("HOPPlop Linear Regression Analyysi")

# Hakee ja käsittelee datan
data, numeric_columns, selected_units = fetch_data()
unit_avg, national_avg = calculate_averages(data, numeric_columns)

# Valitse kysymys
selected_question = st.selectbox("Valitse kysymys", numeric_columns)

# Luo lineaarisen regression visualisointi
def create_plotly_chart(data, selected_unit, selected_question):
    """Visualisoi historialliset tiedot ja ennusteet Plotlyn avulla."""
    unit_data = data[data["unit_code"] == selected_unit]
    
    # Ryhmittele keskiarvot kvartaaleittain
    avg_data = unit_data.groupby("quarter")[selected_question].mean().reset_index()
    avg_data = sort_quarters(avg_data)  # Järjestetään kvartaaleittain

    # Poista rivit, joissa on NaN-arvoja
    avg_data = avg_data.dropna(subset=[selected_question])

    # Tarkista, että datassa on riittävästi pisteitä
    if avg_data.shape[0] > 1:
        # Muodosta X ja y
        X = np.arange(avg_data.shape[0]).reshape(-1, 1)
        y = avg_data[selected_question]
        st.dataframe(X)
        st.dataframe(y)
        # Lineaarinen regressiomalli
        model = LinearRegression()
        model.fit(X, y)

        # Ennusta seuraavat 5 kvartaalia
        last_quarter = avg_data['quarter'].iloc[-1]
        future_quarters = generate_future_quarters(last_quarter, 5)
        future_X = np.arange(len(X), len(X) + len(future_quarters)).reshape(-1, 1)
        st.write(future_quarters)
        st.write(future_X)
        predictions = model.predict(future_X)

        # Luo Plotly-kaavio
        fig = go.Figure()

        # Lisää historiallinen data
        fig.add_trace(go.Scatter(
            x=avg_data['quarter'],
            y=y,
            mode='lines+markers',
            name='Historiallinen data',
            line=dict(color='blue'),
            marker=dict(size=8)
        ))

        # Lisää ennusteet
        fig.add_trace(go.Scatter(
            x=future_quarters,
            y=predictions,
            mode='lines+markers',
            name='Ennusteet',
            line=dict(color='red', dash='dash'),
            marker=dict(size=8, symbol='x')
        ))

        # Kaavion asetukset
        fig.update_layout(
            title=f"{selected_unit} - {selected_question} - Asiakaspalautteen keskiarvot",
            xaxis=dict(title="Kvartaali (vuosi)", tickangle=-45),
            yaxis=dict(title="Keskiarvo"),
            legend=dict(title="Selite"),
            template="plotly_white"
        )

        return fig
    else:
        print(f"Ei riittävästi dataa ennustamiseen kysymykselle {selected_question} yksikölle {selected_unit}.")
        return None

# Näytä lineaarisen regression visualisointi Streamlitissä
selected_unit = st.selectbox("Valitse yksikkö", selected_units)
chart = create_plotly_chart(data, selected_unit, selected_question)
if chart is not None:
    st.plotly_chart(chart)  # Korjattu: Käytetään st.plotly_chart
else:
    st.warning(f"Ei riittävästi dataa ennustamiseen kysymykselle {selected_question} yksikölle {selected_unit}.")
