import streamlit as st
import pandas as pd
from db import get_connection, run_query

# ======================== Page setup ========================

st.set_page_config(
    page_title="Gestion Hôtelière - Agences",
    page_icon="🏢",
    layout="wide"
)

# ======================== Color palette ========================
# Palette: https://colorhunt.co/palette/1b3c53234c6a456882e3e3e3

st.markdown("""
<style>
    .main {
        background-color: #E3E3E3;
    }
    h1, h2, h3 {
        color: #1B3C53;
    }
    .stMetric {
        background-color: #FFFFFF;
        padding: 12px;
        border-radius: 10px;
        border-left: 6px solid #234C6A;
    }
    .stButton > button {
        background-color: #234C6A;
        color: white;
        border-radius: 8px;
        padding: 10px 22px;
        font-size: 15px;
    }
    .stButton > button:hover {
        background-color: #1B3C53;
    }
</style>
""", unsafe_allow_html=True)

# ======================== Title ========================

st.title("🏢 Gestion des Agences de Voyage")
st.markdown("---")

# ======================== Data loading ========================

sql_agences = """
SELECT
    a.Cod_A AS code_agence,
    a.telephone,
    a.site_web,
    a.Adresse_Rue_A,
    a.Adresse_Num_A,
    a.Adresse_Code_Postal,
    a.Adresse_Pays_A,
    v.nom AS ville,
    v.latitude,
    v.longitude,
    v.region,
    v.pays
FROM AGENCE a
JOIN VILLE v ON a.VILLE_Id_ville = v.Id_ville
"""

try:
    df_agences = run_query(sql_agences)
except RuntimeError as e:
    st.error("❌ Erreur lors de l'accès à la base de données")
    st.exception(e)
    st.stop()

if df_agences.empty:
    st.warning("⚠️ Aucune agence trouvée dans la base")
    st.stop()

# ======================== Calculated columns ========================

df_agences["adresse_complete"] = (
    df_agences["Adresse_Rue_A"] + " " +
    df_agences["Adresse_Num_A"] + ", " +
    df_agences["Adresse_Code_Postal"] + ", " +
    df_agences["ville"] + ", " +
    df_agences["Adresse_Pays_A"]
)

# ======================== SECTION 1 : Metrics ========================

st.header("📊 Statistiques des agences")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Nombre d'agences", df_agences["code_agence"].nunique())

with col2:
    st.metric("Nombre de villes", df_agences["ville"].nunique())

with col3:
    ville_top = df_agences["ville"].value_counts()
    st.metric(
        f"Ville la plus représentée ({ville_top.idxmax()})",
        ville_top.max()
    )

st.markdown("---")

# ======================== SECTION 2 : Map ========================

st.header("🗺️ Localisation géographique")

st.map(df_agences[["latitude", "longitude"]])

st.markdown("---")

# ======================== SECTION 3 : Table ========================

st.header("📋 Liste des agences")

table_agences = df_agences[[
    "code_agence",
    "adresse_complete",
    "telephone",
    "site_web"
]].copy()

table_agences.columns = [
    "Code agence",
    "Adresse complète",
    "Téléphone",
    "Site web"
]

st.dataframe(table_agences, use_container_width=True)

st.markdown("---")

# ======================== SECTION 4 : Filter by city ========================

st.header("🔍 Filtrer par ville")

villes = ["Toutes"] + sorted(df_agences["ville"].unique())
ville_selectionnee = st.selectbox("Choisissez une ville :", villes)

if ville_selectionnee != "Toutes":
    df_filtre = df_agences[df_agences["ville"] == ville_selectionnee]

    st.write(f"**{len(df_filtre)} agence(s) trouvée(s)**")

    for _, agence in df_filtre.iterrows():
        with st.expander(f"🏢 {agence['code_agence']}"):
            st.write(f"📍 **Adresse :** {agence['adresse_complete']}")
            st.write(f"📞 **Téléphone :** {agence['telephone']}")
            st.write(f"🌐 **Site web :** {agence['site_web']}")

# ======================== Footer ========================

st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#1B3C53;">
    <p>Application de gestion hôtelière – Module Agences</p>
</div>
""", unsafe_allow_html=True)
