import streamlit as st
import requests
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

st.set_page_config(
    page_title= "Tilastoja",
    page_icon= "🔢",
    layout= "wide"
)

st.title("📟 Tilastoja")
st.markdown("""
            Tällä sivulla näkyy HOPP ja NES datan tilastoja.
            
            Tilastot on luotu Gold-tason datalla.
""")

st.header("🌲 Kainuu vs muu Suomi 🇫🇮")

st.markdown("""
            Tässä analyysissä vertaillaan **Kainuun** ja **muun Suomen** *HOPP*-datan asiakastyytyväisyyden keskiarvoja, ja käytämme **T-testiä** arvioidaksemme, ovatko erot merkittäviä.

            **T-testi** on tilastollinen testi, jolla voidaan vertailla kahden ryhmän, kuten **Kainuun** ja **muun Suomen**, välillä olevia eroja.

            **T-arvo** kuvaa kahden ryhmän välisen eron suuruuden verrattuna ryhmien sisäiseen vaihteluun. **P-arvo** kertoo, kuinka todennäköistä on, että tulokset ovat syntyneet sattumalta.

            Jos **T-arvo** on suuri ja **P-arvo** on pieni, ryhmien ero on suuri ja tilastollisesti merkitsevä.

            Valitse alla analysoitava kysymys, jolloin sen kysymyksen tulokset näytetään.
""")

# Haetaan APIsta dataa
endpoint_gold_hopp = "http://database:8081/get/gold/hopp"

# Funktio hakee datan apista
@st.cache_data
def fetch_data(endpoint, dataset_name):
    response = requests.get(endpoint)
    if response.status_code == 200:
        json_data = response.json()
        data = pd.DataFrame(json_data)
        return data
    else:
        st.error(f"Error: {dataset_name}, {response.text}")
        return None

# Luodaan dataframe apista haetusta datasta
df = fetch_data(endpoint_gold_hopp, "Gold HOPP Data")

# Varmistetaan että ei ole tyhjä
if df is not None:
    # Pudotetaan turhat sarakkeet
    df.drop(['_ts', '_attachments', '_etag', '_self', '_rid', 'id', '/medallion'], axis=1, inplace=True)
    # Näissä 3 kysymyksessä Kainuun rivillä 10 oli None, joten korvasin ne muiden rivien lukuarvoilla ja ottamalla niistä keskiarvon
    kainuu_mean_6 = df.iloc[8:14]['6_hoitajat_kertoivat_minulle_uuden_laakkeen_antamisen_yhteydessa_miksi_laaketta_annetaan'].mean()
    kainuu_mean_7 = df.iloc[8:14]['7_hoitajat_kertoivat_minulle_saamieni_laakkeiden_mahdollisista_sivuvaikutuksista'].mean()
    kainuu_mean_11 = df.iloc[8:14]['11_hoitajat_huolehtivat_etteivat_hoito_ja_tai_tutkimukset_aiheuttaneet_minulle_noloja_tai_kiusallisia_tilanteita'].mean()
    # Lisätään uudet keskiarvot None rivien tilalle
    df['6_hoitajat_kertoivat_minulle_uuden_laakkeen_antamisen_yhteydessa_miksi_laaketta_annetaan'] = df['6_hoitajat_kertoivat_minulle_uuden_laakkeen_antamisen_yhteydessa_miksi_laaketta_annetaan'].fillna(kainuu_mean_6)
    df['7_hoitajat_kertoivat_minulle_saamieni_laakkeiden_mahdollisista_sivuvaikutuksista'] = df['7_hoitajat_kertoivat_minulle_saamieni_laakkeiden_mahdollisista_sivuvaikutuksista'].fillna(kainuu_mean_7)
    df['11_hoitajat_huolehtivat_etteivat_hoito_ja_tai_tutkimukset_aiheuttaneet_minulle_noloja_tai_kiusallisia_tilanteita'] = df['11_hoitajat_huolehtivat_etteivat_hoito_ja_tai_tutkimukset_aiheuttaneet_minulle_noloja_tai_kiusallisia_tilanteita'].fillna(kainuu_mean_11)
    # Valitaan vain nämä sarakkeet
    kysymykset = [col for col in df.columns if col not in ['datajoukko', 'quarter']]
    # Voidaan valita kysymys
    kysymys = st.selectbox("Valitse kysymys", kysymykset)
    # Kainuun datajoukko
    kainuu = df[df['datajoukko'] == 'kainuu']
    # Muun Suomen datajoukko
    muu_suomi = df[df['datajoukko'] == 'kooste']

    # Käytetään Scipy moduulia laskemaan T-testi
    t_stat, p_value = stats.ttest_ind(kainuu[kysymys], muu_suomi[kysymys])
    
    # Kun st.Button painaa uudelleen, niin teksti menee piiloon
    if 'show_text' not in st.session_state:
        st.session_state.show_text = False

    col3, col4 = st.columns(2)
    with col3:
        container = st.container(border=True)
        container.info("T-arvo")
        container.markdown(f'<h2 style="font-size:30px;">{t_stat:.3f}</h2>', unsafe_allow_html=True)
        if st.button("T-arvon info"):
            st.session_state.show_text = not st.session_state.show_text
            if st.session_state.show_text:
                container = st.container(border=True)
                container.write("Esimerkiksi T-arvo = 2 tarkoittaa, että ryhmien keskiarvojen ero on 2 kertaa suurempi, kuin ryhmien sisäinen vaihtelu.")
                container.latex(r'''t = \frac{\bar{X} - \bar{Y}}{\sqrt{\frac{\bar{Var(X)}}{n_x} + \frac{\bar{Var(Y)}}{n_y}}}''')

    with col4:
        container = st.container(border=True)
        container.info("P-arvo")
        container.markdown(f'<h1 style="font-size:30px;">{p_value:.3f}</h1>', unsafe_allow_html=True)
        if st.button("P-arvon info"):
            st.session_state.show_text = not st.session_state.show_text
            if st.session_state.show_text:
                container = st.container(border=True)
                container.write("Esimerkiksi P-arvo = 0.05 tarkoittaa, että jos nollahypoteesi on totta, on 5% todennäköisyys saada tulos sattumalta.")
                container.latex(r'''
                                p < 0.05 \text{ ... tulos on melkein merkitsevä} \\
                                p< 0.01 \text{ ... tulos on merkitsevä} \\
                                p < 0.001 \text{ ... tulos on erittäin merkitsevä}''')

    if p_value < 0.001:
        st.success("TULOS: Ero Kainuun ja muun Suomen välillä on tilastollisesti erittäin merkitsevä!!! (p < 0.001).")
    elif p_value < 0.01:
        st.success("TULOS: Ero Kainuun ja muun Suomen välillä on tilastollisesti merkitsevä! (p < 0.01).")
    elif p_value < 0.05:
        st.success("TULOS: Ero Kainuun ja muun Suomen välillä on tilastollisesti melkein merkitsevä (p < 0.05).")
    else:
        st.success("TULOS: Ero Kainuun ja muun Suomen välillä ei ole tilastollisesti merkitsevä.")

col1, col2 = st.columns(2)
with col1:
    st.header("🌲 Kainuu")

with col2:
    st.header("🇫🇮 Suomi")
