import streamlit as st
import pandas as pd
import requests
import plotly.graph_objs as plt

st.set_page_config(
    page_title= "Käppyrää",
    page_icon= "📈",
    layout= "wide"
)

st.markdown("""
# HOPPlop Interaktiivinen Visualisointi

Tämä työkalu näyttää terveydenhuollon yksiköiden (AIKTEHOHO, EALAPSAIK, ENSIHOITO) palautedatan vertailun vuosineljänneksittäin.

### Ominaisuudet:
- Vertaa yksiköiden tuloksia kansalliseen keskiarvoon
- Interaktiivinen viivakaavio kysymyskohtaisesti
- Värikoodatut viivat eri yksiköille
- Tarkemmat arvot näkyvät viemällä hiiren datapisteiden päälle

### Käyttö:
Valitse haluamasi kysymys pudotusvalikosta nähdäksesi sen tulokset eri yksiköissä ajan mittaan. Kansallinen keskiarvo näytetään mustalla katkoviivalla.
""")

# Asetetaan API-osoite
api_url = "http://database:8081/get/silver/hopp"

@st.cache_data
def fetch_data():
    """Hakee datan REST-API:n kautta ja käsittelee sen."""
    response = requests.get(api_url)
    if response.status_code == 200:
        data = pd.DataFrame(response.json())
        # Määritä numeeriset sarakkeet (kysymykset 1-22)
        numeric_columns = [col for col in data.columns if col.split('_')[0].isdigit()]
        # Suorita vastaavat käsittelyt kuin alkuperäisessä koodissa
        selected_units = ["AIKTEHOHO", "EALAPSAIK", "ENSIHOITO"]
        data = data[data["unit_code"].isin(selected_units)]
        # Korvaa 'E' arvot NaN:lla ja muunna numerot
        data[numeric_columns] = data[numeric_columns].replace('E', pd.NA)
        data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors='coerce')
        return data, numeric_columns, selected_units
    else:
        st.error(f"Virhe haettaessa dataa: {response.status_code}")
        response.raise_for_status()

def sort_quarters(df):
    """Järjestää vuosineljännekset oikeaan järjestykseen."""
    def quarter_to_float(q):
        quarter, year = q.split('_')
        return float(year) + (float(quarter) - 1) / 4

    if isinstance(df.index, pd.MultiIndex):
        quarter_level = 1
        sorted_quarters = sorted(df.index.levels[quarter_level], key=quarter_to_float)
        return df.reindex(level=quarter_level, labels=sorted_quarters)
    else:
        return df.reindex(sorted(df.index, key=quarter_to_float))

def calculate_averages(data, numeric_columns):
    """Laskee yksikkö- ja kansalliset keskiarvot."""
    unit_avg = data.groupby(['unit_code', 'quarter'])[numeric_columns].mean()
    national_avg = data.groupby('quarter')[numeric_columns].mean()
    
    # Muunna indeksit tavalliseksi DataFrame:iksi helpompaa käsittelyä varten
    unit_avg_reset = sort_quarters(unit_avg).reset_index()
    national_avg_reset = sort_quarters(national_avg).reset_index()
    
    return unit_avg_reset, national_avg_reset

# Hakee ja käsittelee datan
data, numeric_columns, selected_units = fetch_data()
unit_avg, national_avg = calculate_averages(data, numeric_columns)

# Valitse kysymys
selected_question = st.selectbox("Valitse kysymys", numeric_columns)

# Luo interaktiivinen Plotly-kaavio
def create_line_race_chart(unit_avg, national_avg, selected_question):
    # Luo viivat jokaiselle yksikölle
    traces = []
    
    # Kansallinen keskiarvo mustalla katkoviivalla
    traces.append(
        plt.Scatter(
            x=national_avg['quarter'], 
            y=national_avg[selected_question], 
            mode='lines+markers',
            name='Kansallinen keskiarvo',
            line=dict(color='black', dash='dot'),
            hovertemplate='Kansallinen: %{y:.2f}<extra></extra>'
        )
    )
    
    # Yksikkökohtaiset viivat
    colors = ['blue', 'green', 'red']  # Voit muokata värejä
    for i, unit in enumerate(selected_units):
        unit_data = unit_avg[unit_avg['unit_code'] == unit]
        traces.append(
            plt.Scatter(
                x=unit_data['quarter'], 
                y=unit_data[selected_question], 
                mode='lines+markers',
                name=unit,
                line=dict(color=colors[i % len(colors)]),
                hovertemplate=f'{unit}: %{{y:.2f}}<extra></extra>'
            )
        )
    
    # Layout-asetukset
    layout = plt.Layout(
        title=f'{selected_question} - Yksikköjen kehitys',
        xaxis=dict(title='Vuosineljännes', tickangle=45),
        yaxis=dict(title='Keskiarvo'),
        hovermode='closest',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Luo figuurin
    fig = plt.Figure(data=traces, layout=layout)
    
    return fig

# Näytä interaktiivinen kaavio
st.plotly_chart(create_line_race_chart(unit_avg, national_avg, selected_question), use_container_width=True)