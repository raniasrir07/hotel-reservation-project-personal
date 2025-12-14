import streamlit as st
from db import run_query

st.set_page_config(page_title="Agences", layout="wide")
st.title("🏢 Agences")

st.info("Affichage READ minimal pour valider la connexion DB.")

try:
    df = run_query("""
        SELECT
            a.Cod_A,
            a.telephone,
            a.site_web,
            a.Adresse_Code_Postal,
            a.Adresse_Rue_A,
            a.Adresse_Num_A,
            a.Adresse_Pays_A,
            v.nom AS ville,
            v.region,
            v.pays
        FROM AGENCE a
        JOIN VILLE v ON v.Id_ville = a.VILLE_Id_ville
        ORDER BY a.Cod_A;
    """)
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error("Erreur chargement agences")
    st.code(str(e))
