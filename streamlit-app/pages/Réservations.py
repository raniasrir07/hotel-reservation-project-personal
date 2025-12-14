import streamlit as st
from db import run_query

st.set_page_config(page_title="Réservations", layout="wide")
st.title("📅 Réservations")

st.info("Affichage READ minimal pour valider la connexion DB.")

try:
    df = run_query("""
        SELECT
            r.CHAMBRE_Cod_C AS chambre,
            r.date_debut,
            r.date_fin,
            r.prix,
            a.Cod_A AS agence,
            v.nom AS ville
        FROM RESERVATION r
        JOIN AGENCE a ON a.Cod_A = r.AGENCE_Cod_A
        JOIN VILLE v ON v.Id_ville = a.VILLE_Id_ville
        ORDER BY r.date_debut DESC;
    """)
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error("Erreur chargement réservations")
    st.code(str(e))

