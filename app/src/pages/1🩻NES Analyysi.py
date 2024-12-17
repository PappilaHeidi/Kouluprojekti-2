import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title= "NES_Analyysi",
    page_icon= "🩺",
    layout= "wide"
)

st.logo("https://kamk.fi/wp-content/uploads/2024/05/K-logo_rgb_150dpi10686.png", size="large")

# API URL
api_url = "http://database:8081/get/bronze/nes"

# Funktio datan hakemiseen
@st.cache_data
def fetch_data():
    """Hakee datan API:sta ja palauttaa sen DataFrame-muodossa."""
    response = requests.get(api_url)
    response.raise_for_status()
    data = pd.DataFrame(response.json())
    return data

# Ladataan data
try:
    data = fetch_data()
    st.success("Data haettu onnistuneesti!")
except Exception as e:
    st.error(f"Virhe datan haussa: {e}")
    st.stop()

# Esikäsittely
data = data.dropna(subset=['year', 'dataset'])
data['year'] = pd.to_numeric(data['year'], errors='coerce')
data['dataset'] = data['dataset'].str.strip().str.lower()

# Suodatetaan halutut vuodet ja datasetit
filtered_data = data[(data['year'].isin([2023, 2024])) & (data['dataset'].isin(['raaka', 'summa']))]

# Jaotellaan data
data_2023 = filtered_data[(filtered_data['year'] == 2023) & (filtered_data['dataset'] == 'raaka')]
data_2024 = filtered_data[(filtered_data['year'] == 2024) & (filtered_data['dataset'] == 'raaka')]
kansallinen_data = filtered_data[filtered_data['dataset'] == 'summa']

# Valitut yksiköt ja kysymykset
yksikot = ['AIKTEHOHO', 'EALAPSAIK', 'ENSIHOITO']
kysymykset = [
    'org_johto_arvojen_muk', 'lahiesimies_avoin_ehdotuksille',
    'lahiesimies_hlokunnan_puolestapuhuja', 'jyh_edustaa_ht_nakyvasti',
    'org_huomioi_hoitajien_ehd', 'kiitosta_tyosta',
    'uskon_org_paamaariin', 'org_innostaa', 'suosittelen_org',
    'ylpea_ammatistani', 'tyoskentelen_3v_todnak',
    'tietoa_org_suu_ja_tav', 'saannollinen_palaute',
    'vaikutan_pothoidon_suu_ja_tot', 'sopivasti_itsenainen'
]

# Suodatetaan yksiköiden data
#yksikko_data_2023 = data_2023[data_2023['tyoyksikko'].isin(yksikot)]
#yksikko_data_2024 = data_2024[data_2024['tyoyksikko'].isin(yksikot)]

# Radar-kaavion teemat
mapping = {
    'Laadukkaan ammatillisen toiminnan perusteet': ['hoitajat_taitavia', 'hoitajat_npt_kayttoon', 'noudatan_np_toimohjeita'],
    'Johtaminen': ['org_johto_arvojen_muk', 'jyh_edustaa_ht_nakyvasti'],
    'Autonomia': ['sopivasti_itsenainen', 'vaikutan_pothoidon_suu_ja_tot'],
    'Moniammatillinen yhteistyo': ['laakarit_arvostavat_hoitajia', 'osall_laak_kanssa_pothoidon_paat'],
    'Hoitajien valinen yhteistyo': ['hyvat_suhteet_hoitajiin', 'tukea_avustavalta_hlokunnalta'],
    'Ammatillinen kasvu': ['amm_kasvu_merkittavaa', 'org_tarjoaa_urallakehitt_mahd'],
    'Tyonteossa tarvittavat resurssit': ['kaytettavissa_tarv_laitteet', 'sopivasti_potilaita', 'riittavasti_aikaa_pot'],
    'Muut sitoutumiseen vaikuttavat tekijat': ['org_innostaa', 'suosittelen_org'],
    'Sitoutuneisuus': ['ylpea_ammatistani', 'tyoskentelen_3v_todnak']
}

def visualisoi_keskiarvojen_vertailu(yksikko, kysymys):
    global data_2023, data_2024  # Varmista, että käytetään globaaleja muuttujia
    
    # Poista puuttuvat arvot suoraan käsittelyssä
    yksikko_2023 = data_2023.dropna(subset=[kysymys])
    yksikko_2024 = data_2024.dropna(subset=[kysymys])
    
    # Suodata valittu yksikkö
    yksikko_2023 = yksikko_2023[yksikko_2023['tyoyksikko'] == yksikko]
    yksikko_2024 = yksikko_2024[yksikko_2024['tyoyksikko'] == yksikko]
    
    # Tarkista, että valittu kysymys löytyy datasta
    if kysymys not in yksikko_2023.columns or kysymys not in yksikko_2024.columns:
        st.error(f"Kysymystä '{kysymys}' ei löydy datasta.")
        return
    
    # Laske keskiarvot
    mean_2023 = yksikko_2023[kysymys].mean(skipna=True)
    mean_2024 = yksikko_2024[kysymys].mean(skipna=True)

    # Tarkista keskiarvot
    if pd.isna(mean_2023) or pd.isna(mean_2024):
        st.warning("Keskiarvoa ei voitu laskea. Tarkista datan arvot.")
        return

    fig = go.Figure()

    # Lisää viiva 2023 vuoden keskiarvoille
    fig.add_trace(go.Scatter(
        x=[2023, 2024],
        y=[mean_2023, mean_2024],
        mode='lines+markers',
        name=yksikko,
        line=dict(color='blue', dash='solid'),
        marker=dict(color='blue', size=8),
    ))

    # Asetetaan otsikko ja akselien nimet
    fig.update_layout(
        title=f"Yksikön {yksikko} keskiarvojen vertailu kysymykselle '{kysymys}'",
        xaxis_title="Vuosi",
        yaxis_title="Keskiarvo (asteikko 1-6)",
        yaxis=dict(range=[1, 6]),
        template="plotly_white",  # Valkoinen tausta
        showlegend=True,
        xaxis=dict(tickmode='array', tickvals=[2023, 2024]),
        plot_bgcolor='white'
    )

    # Näytetään kaavio Streamlitissä
    st.plotly_chart(fig)


# Radar-kaavio
def visualisoi_radar(yksikko):
    def laske_teemakeskiarvot(data):
        grouped_means = {}
        for group, columns in mapping.items():
            valid_columns = [col for col in columns if col in data.columns]
            grouped_means[group] = data[valid_columns].mean(axis=1)
        return pd.DataFrame(grouped_means).mean()

    teemat_2023 = laske_teemakeskiarvot(data_2023[data_2023['tyoyksikko'] == yksikko])
    teemat_2024 = laske_teemakeskiarvot(data_2024[data_2024['tyoyksikko'] == yksikko])

    labels = teemat_2023.index
    values_2023 = teemat_2023.values.tolist() + [teemat_2023.values[0]]
    values_2024 = teemat_2024.values.tolist() + [teemat_2024.values[0]]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    st.header("📡 Radar-kaavio: Teemojen vertailu")
    st.markdown("""**Radar-kaavio** antaa visuaalisen kuvan, jossa näkyy eri teemojen (esim. johtaminen, työolosuhteet, tiimityö) kehitys, ja se havainnollistaa, miten valitun yksikön suoritustaso on muuttunut ajassa.
                
Valitse sivupalkista yksikkö, jonka teemoja haluat tarkastella.
                
""")

    # Lasketaan kulmat, jotka jakavat ympyrän tasaisesti
    angles = [n / float(len(labels)) * 2 * 3.141592653589793 for n in range(len(labels))]
    angles += angles[:1]  # Suljetaan ympyrä

    # Luodaan radar-kaavio Plotlyllä
    fig = go.Figure()

    # 2023 data
    fig.add_trace(go.Scatterpolar(
        r=values_2023 + [values_2023[0]],  # Suljetaan ympyrä
        theta=labels,  # Suljetaan ympyrä
        fill='toself',  # Täyttää alueen
        name='2023',
        line=dict(color='blue', dash='dash')  # Tyylitellään viiva
    ))

    # 2024 data
    fig.add_trace(go.Scatterpolar(
        r=values_2024 + [values_2024[0]],  # Suljetaan ympyrä
        theta=labels,  # Suljetaan ympyrä
        fill='toself',  # Täyttää alueen
        name='2024',
        line=dict(color='red')  # Tyylitellään viiva
    ))

    # Asetetaan otsikko ja muut visuaaliset asetukset
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                color="black",
                range=[0, 6]  # Asteikko 1-6
            )
        ),
        title="Radar-kaavio: 2023 vs 2024",
        showlegend=True
    )

    # Näytetään kaavio Streamlitissä
    st.plotly_chart(fig)

def visualisoi_kansalliset_keskiarvot():
        st.header("🇫🇮 Kansalliset keskiarvot")
        st.markdown("""
        Kansalliset keskiarvot tarjoavat vertailukohdan yksiköiden ja teemojen tuloksille.  
                    
        Voit arvioida, miten yksikkösi suoriutuu suhteessa kansalliseen keskiarvoon.
        """)

        # Valitut teemat (muokkaa tarvittaessa)
        kysymykset_kansallinen = [
            'laadukkaan_ammatillisen_toiminnan_perusteet', 'johtaminen',
            'autonomia', 'moniammatillinen_yhteistyo', 'hoitajien_valinen_yhteistyo',
            'ammatillinen_kasvu', 'tyonteossa_tarvittavat_resurssit',
            'muut_sitoutumiseen_vaikuttavat_tekijat', 'sitoutuneisuus'
        ]

        # Tarkista, että kansallinen_data sisältää tarvittavat sarakkeet
        kansallinen_cleaned = kansallinen_data[kysymykset_kansallinen].apply(pd.to_numeric, errors='coerce')
        kansallinen_mean = kansallinen_cleaned.mean()

        # Muodostetaan DataFrame, jotta voidaan käyttää bar_chart
        df_kansallinen = kansallinen_mean.reset_index()
        df_kansallinen.columns = ['Teema', 'Keskiarvo']

        # Plotly pylväsdiagrammi
        fig = px.bar(df_kansallinen, x='Teema', y='Keskiarvo', title="Kansalliset keskiarvot teemoille", color_discrete_sequence=["#002F6C"],
                    labels={'Teema': 'Teemat', 'Keskiarvo': 'Keskiarvo (asteikko 1-6)'})
        
        st.plotly_chart(fig)


# Käyttöliittymä
st.title("🩻 NES Kyselytulosten Visualisointi")

st.markdown("""      
    Tältä sivulta löytyy analysointityökalu **NES**-datalle, eli henkilöstön työtyytyväisyyskyselyyn.

    Analysoinnissa voit tarkastella yksittäisiä kysymyksiä, teemojen kokonaisuuksia sekä suhteuttaa tuloksia kansalliseen tasoon.
            
    ### Käytön vaiheet:
            
    1. **Valitse yksikkö ja kysymys sivupalkista:**
            
        * Sivupalkin valinnat ohjaavat viivakaavion ja radar-kaavion sisältöä.
    
        * Yksikön ja kysymyksen valinnan jälkeen keskiarvot lasketaan ja kaaviot päivittyvät.
            
    2. **Analysoi viivakaavion kehitystä:**
            
        * Tuloksia voidaan tarkastella ajan suhteen yksittäisen kysymyksen osalta.
            
    3. **Tarkastele teemojen kokonaisuutta radar-kaaviolla:**
            
        * Radar-kaavio antaa kokonaiskuvan teemojen vahvuuksista ja muutoksista.
            
    4. **Vertaa kansalliseen keskiarvoon:**
            
        * Pylväsdiagrammilla saat yleiskuvan kansallisista tuloksista.
""")

# Valinnat sivupalkissa
selected_unit = st.sidebar.selectbox("Valitse yksikkö:", yksikot)
selected_question = st.sidebar.selectbox("Valitse kysymys:", kysymykset)

# Keskiarvot yksittäiselle kysymykselle
st.header("📈 Viivakaavio: Keskiarvojen tarkastelu")
st.markdown("""
    **Viivakaavio** näyttää valitun yksikön keskiarvon muutoksen tietyssä kysymyksessä vuosina 2023 ja 2024, tarjoten visuaalisen kuvan siitä, onko työtyytyväisyys parantunut, heikentynyt vai pysynyt ennallaan.

    Valitse sivupalkista yksikkö ja kysymys, joita haluat tarkastella. 
""")
visualisoi_keskiarvojen_vertailu(selected_unit, selected_question)

# Radar-kaavio
visualisoi_radar(selected_unit)

# Kansalliset keskiarvot
visualisoi_kansalliset_keskiarvot()


#st.write("Vuoden 2023 sarakkeet:", data_2023.columns)
#st.write("Vuoden 2024 sarakkeet:", data_2024.columns)
