import streamlit as st
import requests
import pandas as pd
from scipy import stats
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title= "Tilastoja",
    page_icon= "🔢",
    layout= "wide"
)

st.logo("https://kamk.fi/wp-content/uploads/2024/05/K-logo_rgb_150dpi10686.png", size="large")

st.title("📟 Tilastoja")
st.markdown("""
            Tältä sivulta löytyy erilaisia tilastoja, joissa vertaillaan **Kainuun** ja **Kansallisia** tuloksia.
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
    # Kainuun datajoukko
    kainuu = df[df['datajoukko'] == 'kainuu']
    # Muun Suomen datajoukko
    muu_suomi = df[df['datajoukko'] == 'kooste']
    # Varmitstetaan että kvarttaalit ovat uniikkeja (Vaikka ne on jo)
    kvarttaalit = df['quarter'].unique()
    # Voidaan valita kysymys

    # Kainuun ja Muun Suomen tietojen erottaminen kvartaalikohtaisesti
    combined_data_kainuu = kainuu[['quarter', 'datajoukko'] + kysymykset]
    combined_data_muu_suomi = muu_suomi[['quarter', 'datajoukko'] + kysymykset]

    # Streamlitin visualisointi
    st.header("❓ Kainuun ja Kansallisten kysymysten keskiarvot kvartaaleittain")

    st.markdown("""
    Tässä analyysissä vertaillaan **Kainuun** ja **Kansallisten** kysymysten keskiarvoja kvartaaleittain. 
    
    Keskiarvot on laskettu kyselyn tuloksista ja ne kuvaavat **Kainuun** ja **muun Suomen** asiakastyytyväisyyttä.

    Analyysi havainnollistaa, miten kysymysten vastaukset muuttuvat eri kvartaaleittain.
""")

    col1, col2 = st.columns(2)

    with col1:
        # Kainuun visualisointi kvartaaleittain
        st.subheader("🌲 Kainuun keskiarvot")
        kainuu_long = pd.melt(combined_data_kainuu,
                            id_vars=['quarter', 'datajoukko'], 
                            value_vars=kysymykset,
                            var_name='Kysymys', 
                            value_name='Keskiarvo'
        )
        st.bar_chart(kainuu_long, x="quarter", y="Keskiarvo", color="Kysymys", use_container_width=True, horizontal=True)

    with col2:
        # Muun Suomen visualisointi kvartaaleittain
        st.subheader("🇫🇮 Kansalliset keskiarvot")
        muu_suomi_long = pd.melt(combined_data_muu_suomi,
                                id_vars=['quarter', 'datajoukko'],
                                value_vars=kysymykset,
                                var_name='Kysymys',
                                value_name='Keskiarvo'
        )
        st.bar_chart(muu_suomi_long, x="quarter", y="Keskiarvo", color="Kysymys", use_container_width=True, horizontal=True)

    col3, col4, col5, col6 = st.columns(4)
    
    # Etsitään Kainuun parhain keskiarvo
    kainuu_best = kainuu_long.loc[kainuu_long['Keskiarvo'].idxmax()]
    # Paras keskiarvo
    value_kainuu_best = f'{kainuu_best['Keskiarvo']:.2f}'
    # Parhaan keskiarvon kysymys
    question_kainuu_best = f'{kainuu_best['Kysymys']}'
    # Parhaan keskiarvon kvartaali
    quarter_kainuu_best = f'{kainuu_best['quarter']}'

    # Etsitään Kainuun huonoin keskiarvo
    kainuu_worst = kainuu_long.loc[kainuu_long['Keskiarvo'].idxmin()]
    # Huonoin keskiarvo
    value_kainuu_worst = f'{kainuu_worst['Keskiarvo']:.2f}'
    # Huonoimman keskiarvon kysymys
    question_kainuu_worst = f'{kainuu_worst['Kysymys']}'
    # Huonoimman keskiarvon kvartaali
    quarter_kainuu_worst = f'{kainuu_worst['quarter']}'

    with col3:
        # Esitetään kainuun paras keskiarvo metriikka
        container = st.container(border=True)
        container.metric(label='🔋 Kainuun parhain keskiarvo', value=value_kainuu_best)
        container.metric(label='Kysymys', value=question_kainuu_best)
        container.metric(label='Kvartaali', value=quarter_kainuu_best)
    with col4:
        # Esitetään kainuun huonoin keskiarvo metriikka
        container = st.container(border=True)
        container.metric(label='🪫 Kainuun huonoin keskiarvo', value=value_kainuu_worst)
        container.metric(label='Kysymys', value=question_kainuu_worst)
        container.metric(label='Kvartaali', value=quarter_kainuu_worst)

    # Etsitään kansallisesti parhain keskiarvo
    suomi_best = muu_suomi_long.loc[muu_suomi_long['Keskiarvo'].idxmax()]  
    # Parhain keskiarvo      
    value_suomi_best = f'{suomi_best['Keskiarvo']:.2f}'
    # Parhaimman keskiarvon kysymys
    question_suomi_best = f'{suomi_best['Kysymys']}'
    # Parhaimman keskiarvon kvartaali
    quarter_suomi_best = f'{suomi_best['quarter']}'

    # Etsitään kansallisesti huonoin keskiarvo
    suomi_worst = muu_suomi_long.loc[muu_suomi_long['Keskiarvo'].idxmin()]
    # Huonoin keskiarvo        
    value_suomi_worst = f'{suomi_worst['Keskiarvo']:.2f}'
    # Hunoimman keskiarvon kysymys
    question_suomi_worst = f'{suomi_worst['Kysymys']}'
    # Hunoimman keskiarvon kvartaali
    quarter_suomi_worst = f'{suomi_worst['quarter']}'

    with col5:
        # Esitetään kansallisesti paras keskiarvo metriikka
        container = st.container(border=True)
        container.metric(label='🔋 Kansallisesti parhain keskiarvo', value=value_suomi_best)
        container.metric(label='Kysymys', value=question_suomi_best)
        container.metric(label='Kvartaali', value=quarter_suomi_best)
    with col6:
        # Esitetään kansallisesti huonoin keskiarvo metriikka
        container = st.container(border=True)
        container.metric(label='🪫 Kansallisesti huonoin keskiarvo', value=value_suomi_worst)
        container.metric(label='Kysymys', value=question_suomi_worst)
        container.metric(label='Kvartaali', value=quarter_suomi_worst)

    st.header("📅 Kainuun ja Kansallisten kyselyiden kvartaali-keskiarvot")
    
    st.markdown("""
    Tässä analyysissä tarkastellaan **Kainuun** ja **Kansallisten** kvarttaaleittaisia keskiarvoja.

    Kvartaalikohtaiset keskiarvot yhdistää kaikkien kysymysten keskiarvot.

    Analyysi havainnollistaa, kuinka asiakastyytyväisyys muuttuu keskimäärin eri kvartaaleittain.
""")

    # Yhdistetään kaikki kansalliset kvartaalit ja keskiarvot ja luodaan uudet keskiarvot per kvartaali
    muu_suomi_grouped = muu_suomi_long.groupby('quarter')['Keskiarvo'].mean().reset_index()
    # Yhdistetään kaikki kainuun kvartaalit ja keskiarvot ja luodaan uudet keskiarvot per kvartaali
    kainuu_grouped = kainuu_long.groupby('quarter')['Keskiarvo'].mean().reset_index()

    # Etsitään kainuun parhain keskiarvo yhdistetystä taulusta
    kainuu_grouped_best = kainuu_grouped.loc[kainuu_grouped['Keskiarvo'].idxmax()]
    # Parhain keskiarvo
    grouped_kainuu_value_best = f'{kainuu_grouped_best['Keskiarvo']:.2f}'
    # Parhaimman keskiarvon kvartaali
    grouped_kainuu_quarter_best = f'{kainuu_grouped_best['quarter']}'

    # Etsitään kainuun huonoin keskiarvo yhdistetystä taulusta
    kainuu_grouped_worst = kainuu_grouped.loc[kainuu_grouped['Keskiarvo'].idxmin()]
    # Huonoin keskiarvo
    grouped_kainuu_value_worst = f'{kainuu_grouped_worst['Keskiarvo']:.2f}'
    # Huonoimman keskiarvon kvartaali
    grouped_kainuu_quarter_worst = f'{kainuu_grouped_worst['quarter']}'

    # Etsitään kansallisesti parhain keskiarvo yhdistetystä taulusta
    muu_suomi_grouped_best = muu_suomi_grouped.loc[muu_suomi_grouped['Keskiarvo'].idxmax()]
    # Parhain keskiarvo
    grouped_suomi_value_best = f'{muu_suomi_grouped_best['Keskiarvo']:.2f}'
    # Parhaimman keskiarvon kvartaali
    grouped_suomi_quarter_best = f'{muu_suomi_grouped_best['quarter']}'

    # Etsitään kansallisesti huonoin keskiarvo yhdistetystä taulusta
    muu_suomi_grouped_worst = muu_suomi_grouped.loc[muu_suomi_grouped['Keskiarvo'].idxmin()]
    # Huonoin keskiarvo
    grouped_suomi_value_worst = f'{muu_suomi_grouped_worst['Keskiarvo']:.2f}'
    # Huonoimman keskiarvon kvartaali
    grouped_suomi_quarter_worst = f'{muu_suomi_grouped_worst['quarter']}'

    col7, col8 = st.columns(2)

    with col7:
        # Esitetään kainuun kvartaali taulukko
        st.bar_chart(kainuu_grouped, x='quarter', y='Keskiarvo', color="#ffa3eb", use_container_width=True)

    with col8:
        # Esitetään kansallinen kvartaali taulukko
        st.bar_chart(muu_suomi_grouped, x="quarter", y="Keskiarvo", color="#35daff", use_container_width=True)

    col9, col10, col11, col12 = st.columns(4)

    with col9:
        # Esitetään kainuun parhain kvartaali keskiarvojen metriikka
        container = st.container(border=True)
        container.metric(label='🔋 Kainuun parhaimman kvartaalin keskiarvo', value=grouped_kainuu_value_best)
        container.metric(label='Kvartaali', value=grouped_kainuu_quarter_best)

    with col10:
        # Esitetään kainuun huonoin kvartaali keskiarvojen metriikka
        container = st.container(border=True)
        container.metric(label='🪫 Kainuun huonoimman kvartaalin keskiarvo', value=grouped_kainuu_value_worst)
        container.metric(label='Kvartaali', value=grouped_kainuu_quarter_worst)
    
    with col11:
        # Esitetään kansallisesti parhain kvartaali keskiarvojen metriikka
        container = st.container(border=True)
        container.metric(label='🔋 Kansallisesti parhaimman kvartaalin keskiarvo', value=grouped_suomi_value_best)
        container.metric(label='Kvartaali', value=grouped_suomi_quarter_best)

    with col12:
        # Esitetään kansallisesti huonoin kvartaali keskiarvojen metriikka
        container = st.container(border=True)
        container.metric(label='🪫 Kansallisesti huonoimman kvartaalin keskiarvo', value=grouped_suomi_value_worst)
        container.metric(label='Kvartaali', value=grouped_suomi_quarter_worst)

    st.header("🌲 Kainuu vs Kansallinen 🇫🇮")

    st.markdown("""
                Tässä analyysissä vertaillaan **Kainuun** ja **muun Suomen** *HOPP*-datan asiakastyytyväisyyden keskiarvoja, ja käytämme **T-testiä** arvioidaksemme, ovatko erot merkittäviä.

                **T-testi** on tilastollinen testi, jolla voidaan vertailla kahden ryhmän, kuten **Kainuun** ja **muun Suomen**, välillä olevia eroja.

                **T-arvo** kuvaa kahden ryhmän välisen eron suuruuden verrattuna ryhmien sisäiseen vaihteluun. **P-arvo** kertoo, kuinka todennäköistä on, että tulokset ovat syntyneet sattumalta.

                Jos **T-arvo** on suuri ja **P-arvo** on pieni, ryhmien ero on suuri ja tilastollisesti merkitsevä.

                Valitse alla analysoitava kysymys, jolloin sen kysymyksen tulokset näytetään.
    """)

    kysymys = st.selectbox("Valitse kysymys", kysymykset)
    # Käytetään Scipy moduulia laskemaan T-testi
    t_stat, p_value = stats.ttest_ind(kainuu[kysymys], muu_suomi[kysymys])
    
    # Kun st.Button painaa uudelleen, niin teksti menee piiloon
    if 'show_text' not in st.session_state:
        st.session_state.show_text = False

    col3, col4 = st.columns(2)
    with col3:
        # Esitetään t-arvo tulokset
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
        # Esitetään p-arvo tulokset
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

# T-jakauman visualisointi
x = np.linspace(-5, 5, 1000)
t_dist = stats.t.pdf(x, df=len(kainuu) + len(muu_suomi) - 2)  # t-jakauma
# Plotly-kuvaaja
fig = go.Figure()
# T-jakauman käyrä
fig.add_trace(go.Scatter(x=x, y=t_dist, mode='lines', name="T-jakauma", line=dict(color='#1e36de')))
# P-arvon alueen korostus
fig.add_trace(go.Scatter(
    x=x[(x >= stats.t.ppf(1 - 0.025, df=len(kainuu) + len(muu_suomi) - 2))],
    y=t_dist[(x >= stats.t.ppf(1 - 0.025, df=len(kainuu) + len(muu_suomi) - 2))],
    fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.8)', name="P-arvon alue (0.05 ja alle)"
))
# P-arvon alue käänteisesti
fig.add_trace(go.Scatter(
    x=x[(x <= stats.t.ppf(0.025, df=len(kainuu) + len(muu_suomi) - 2))],
    y=t_dist[(x <= stats.t.ppf(0.025, df=len(kainuu) + len(muu_suomi) - 2))],
    fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.8)'
))
# P-arvon **vaakaviiva**
p_value_position = stats.t.ppf(1 - p_value, df=len(kainuu) + len(muu_suomi) - 2)
fig.add_trace(go.Scatter(
    x=[-5, 5],  # Vaakaviiva kulkee koko akselin yli
    y=[stats.t.pdf(p_value_position, df=len(kainuu) + len(muu_suomi) - 2)] * 2,  # P-arvon korkeus t-jakaumassa
    mode='lines',
    name=f'P-arvo: {p_value:.3f}',
    line=dict(color='#ffc4e6', dash='dot')
))
# Hypoteesi 0 - pystysuora viiva
fig.add_trace(go.Scatter(x=[0, 0], y=[0, max(t_dist)], mode='lines', name="Hypoteesi 0", line=dict(color='black')))
# T-arvo - pystysuora viiva
fig.add_trace(go.Scatter(x=[t_stat, t_stat], y=[0, max(t_dist)], mode='lines', name=f'T-arvo ({t_stat:.3f})', line=dict(color='#fff228', dash='dash')))
# Otsikko, akselit ja legenda
fig.update_layout(
    title=f"T-jakauma ja t-arvo ({kysymys})",
    xaxis_title="T-arvo",
    yaxis_title="Todennäköisyyden tiheys",
    legend_title="Legenda",
)
# Näytetään kuva Streamlitissä
st.plotly_chart(fig)
