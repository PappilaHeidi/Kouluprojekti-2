import streamlit as st

# Päänäkymä
st.set_page_config(
    page_title="Etusivu",
    page_icon="🏠",
    layout="wide"
)

st.logo("https://kamk.fi/wp-content/uploads/2024/05/K-logo_rgb_150dpi10686.png", size="large")

# Sivun otsikko ja teksti
st.title("🚀 Mojovat: Ennusteita datan pohjalta")

# Tekoälyllä luotu kuva
st.image('/app/src/images/kuva.webp', caption='Kuva on luotu käyttäen OpenAI DALL·E 3 -työkalua.')

st.header("📖 Projektin tarina")
st.markdown(""" 
            **Tässä projektissa tarjoamme Kainuun Hyvinvointialueelle kattavia data-analyysipalveluja, jotka tukevat päätöksentekoa ja edistävät palveluiden kehittämistä. Tavoitteenamme on parantaa henkilöstön hyvinvointia ja asiakastyytyväisyyttä keskittymällä erityisesti seuraaviin osa-alueisiin: johtaminen, sitoutuneisuus ja palvelun laatu.**
            
            Analyysit käsittelevät kahta keskeistä teemaa:
            * **😊 HOPP:** Asiakastyytyväisyys, joka mittaa asiakkaiden kokemuksia eri yksiköiden palveluista.
            * **💼 NES:** Henkilöstön työtyytyväisyys, joka antaa näkökulman työilmapiirin ja sitoutumisen tasoon.
            
            Projektin tavoitteena on tuottaa käytännöllistä ja arvokasta tietoa, joka auttaa Kainuun Hyvinvointialuetta:
            * Parantamaan päätöksentekoa ja resurssien käyttöä.
            * Kehittämään henkilöstön hyvinvointia ja työn laatua.
            * Optimoimaan asiakaspalvelua ja tuottamaan erinomaisia asiakaskokemuksia.
""")

st.header("📜 Tehtävänannot ja Ratkaisuehdotukset")
st.markdown("""
            **😊 HOPP: Asiakastyytyväisyys**

            Analysoimme ja ennustamme `AIKTEHOHO`-, `EALAPSAIK`- ja `ENSIHOITO`-yksiköiden asiakaspalautteita.
            1. **Visualisointi: Keskiarvot ja kansalliset vertailut**

                Näytämme yksiköiden kaikkien kysymysten keskiarvot vuosineljänneksittäin (2021/Q3 - 2023/Q1) ja vertaamme niitä kansallisiin keskiarvoihin. Puuttuva data huomioidaan asianmukaisesti.
            2. **Visualisointi: Vastausten jakauma**

                Esitämme yksiköiden vastausten jakauman eri vuosineljänneksiltä ja nostamme esille keskeiset trendit.
            3. **Ennustus: Keskiarvot seuraavalle vuosineljännekselle (Q4/2023)**

                Ennustamme yksiköiden asiakaspalautteen keskiarvoja, esitellen kaikki aiemmat arvot vertailukohtana.

            4. **Työkalu: Ennustus valitulle kysymykselle**

                Käyttäjä voi valita yksittäisen kysymyksen, jolle ennustetaan arvo Q4/2023. Tuloksissa näkyvät myös kysymyksen kaikki aikaisemmat arvot.
            
            **💼 NES: Henkilöstön työtyytyväisyys**

            Selvitämme työtyytyväisyyden tilaa ja vertaamme yksiköiden tuloksia keskenään sekä kansallisiin keskiarvoihin.

            1. **Visualisointi: Yksiköiden ja kansallisten keskiarvojen vertailu**

                `AIKTEHOHO`-, `EALAPSAIK`- ja `ENSIHOITO`-yksiköiden vastaukset esitetään suhteessa kaikkien yksikköjen ja kansallisiin keskiarvoihin.
            2. **Visualisointi: Vastausten jakauma ja vertailu vuoden 2023 tietoihin**

                Esitämme yksiköiden vastausten jakaumat ja vertaamme niitä vuoden 2023 vastausten jakaumiin.
            3. **Työkalu: Jakauman tarkastelu valitulle kysymykselle**

                Käyttäjä voi valita yksittäisen kysymyksen, jonka vastausjakauma näytetään. Referenssinä käytetään myös edellisen vuoden (2023) jakaumaa.
""")        

st.header("🎉 Projektin lopputulos")

st.markdown("TODO")

# Repositorin linkki
st.header("💾 Repositori")
st.markdown("Tässä linkki GitLab projektin repositoriin")
st.link_button("GitLab", "https://gitlab.dclabra.fi/projekti-2-ml-2024/mojovat/project_sigma")

# Clockify linkki
st.header("⏱️ Clockify")
st.markdown("Tässä Mojovien projektin yhteistunnit")
st.markdown('<iframe src="https://app.clockify.me/shared/673c996fa5b53c67d258d043" width="1000" height="600"></iframe>', unsafe_allow_html=True)

# GitLab stats

st.header("🗂️ GitLab Stats")

st.markdown("TODO")

