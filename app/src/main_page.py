import streamlit as st

# Päänäkymä
st.set_page_config(
    page_title="Pääsivu",
    page_icon="⭐️",
    layout="wide"
)

# Sivun otsikko ja teksti
st.title("⚜️ Mojovat ⚜️")
st.write("Tämä on projektimme pääsivu, joka sisältää ... Tänne vois lisää myös GitLab stats")

# Tekoälyllä luotu kuva
st.image('/app/src/images/kuva.webp', caption='Kuva on luotu käyttäen OpenAI DALL·E 3 -työkalua.')

# Repositorin linkki
st.header("Repositori")
st.link_button("GitLab repositorin linkki", "https://gitlab.dclabra.fi/projekti-2-ml-2024/mojovat/project_sigma")

# Clockify linkki
st.header("Clockify")
st.markdown('<iframe src="https://app.clockify.me/shared/673c996fa5b53c67d258d043" width="1000" height="600"></iframe>', unsafe_allow_html=True)
