import streamlit as st
from db import run_query

st.set_page_config(page_title="Chambres", layout="wide")
st.title("🛏️ Chambres")

st.info("Affichage READ minimal pour valider la connexion DB.")

try:
    df = run_query("""
        SELECT
            Cod_C,
            numero_etage,
            surface
        FROM CHAMBRE
        ORDER BY Cod_C;
    """)
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error("Erreur chargement chambres")
    st.code(str(e))
