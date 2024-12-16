import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests

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

    # Piirrä viivakaavio
    plt.figure(figsize=(10, 6))
    plt.plot([2023, 2024], [mean_2023, mean_2024], marker='o', linestyle='-', color='blue', label=yksikko)

    plt.xticks([2023, 2024])
    plt.xlabel('Vuosi')
    plt.ylabel('Keskiarvo (asteikko 1-6)')
    plt.title(f"Yksikön {yksikko} keskiarvojen vertailu kysymykselle '{kysymys}'")
    plt.ylim(1, 6)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    st.pyplot(plt)


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

    st.subheader("Radar-kaavio: Teemojen vertailu")
    st.markdown("Visualisoi valitun yksikön teemojen keskiarvot vuosina 2023 ja 2024.")

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, values_2023, label="2023", linestyle="--")
    ax.plot(angles, values_2024, label="2024")
    ax.fill(angles, values_2023, alpha=0.2)
    ax.fill(angles, values_2024, alpha=0.4)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.legend(loc="upper right")
    st.pyplot(fig)

def visualisoi_kansalliset_keskiarvot():
        st.subheader("Kansalliset keskiarvot")
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

        # Piirrä pylväsdiagrammi
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(kansallinen_mean.index, kansallinen_mean.values, color='skyblue')
        ax.set_title("Kansalliset keskiarvot teemoille")
        ax.set_ylabel("Keskiarvo (asteikko 1-6)")
        ax.set_xlabel("Teemat")
        plt.xticks(rotation=45, ha='right')
        plt.ylim(1, 6)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)


# Käyttöliittymä
st.title("NES Kyselytulosten Visualisointi")

# Valinnat sivupalkissa
selected_unit = st.sidebar.selectbox("Valitse yksikkö:", yksikot)
selected_question = st.sidebar.selectbox("Valitse kysymys:", kysymykset)

# Keskiarvot yksittäiselle kysymykselle
st.header("Viivakaavio: Keskiarvojen tarkastelu")
visualisoi_keskiarvojen_vertailu(selected_unit, selected_question)

# Radar-kaavio
st.header("Radar-kaavio teemojen vertailulle")
visualisoi_radar(selected_unit)

# Kansalliset keskiarvot
if st.button("Näytä kansalliset keskiarvot"):
    visualisoi_kansalliset_keskiarvot()


#st.write("Vuoden 2023 sarakkeet:", data_2023.columns)
#st.write("Vuoden 2024 sarakkeet:", data_2024.columns)
