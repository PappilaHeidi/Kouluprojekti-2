import streamlit as st

st.set_page_config(
    page_title= "Tilastoja",
    page_icon= "📊",
    layout= "wide"
)

st.title("📟 Tilastoja")
st.markdown("""
            Tällä sivulla näkyy HOPP ja NES datan tilastoja.
            
            Tilastot on luotu Gold-tason datalla.
""")

col1, col2 = st.columns(2)

with col1:
    st.header("💊 HOPP")

with col2:
    st.header("🩺 NES")