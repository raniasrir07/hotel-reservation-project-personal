import streamlit as st
import pandas as pd
import os
from db import run_query

# ======================== Page setup ========================

st.set_page_config(
    page_title="Gestion Hôtelière",
    page_icon="🏨",
    layout="wide"
)

theme_path = os.path.join(os.path.dirname(__file__), '..', 'theme.css')
with open(theme_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ======================== Header ========================

st.title("🏨 Tableau de bord – Gestion Hôtelière")
st.caption("Vue globale des agences & chambres disponibles")
st.divider()

# ======================== DATA : AGENCES ========================

sql_agences = """
SELECT
    a.CodA AS code_agence,
    a.Tel AS telephone,
    a.WebSite AS site_web,
    CONCAT(a.Street_Address, ' ', a.Num_Address, ', ', c.Name) AS adresse_complete,
    c.Name AS ville,
    c.Latitude AS latitude,
    c.Longitude AS longitude
FROM TRAVEL_AGENCY a
JOIN CITY c ON a.City_Address = c.Name
"""

df_agences = run_query(sql_agences)

# ======================== METRICS ========================

st.subheader("📊 Indicateurs clés")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Agences enregistrées", df_agences["code_agence"].nunique())

with c2:
    st.metric("Villes couvertes", df_agences["ville"].nunique())

with c3:
    top_city = df_agences["ville"].value_counts()
    st.metric("Ville dominante", top_city.idxmax())

st.divider()

# ======================== MAP ========================

st.subheader("🗺️ Répartition géographique")

ville_map = st.selectbox(
    "Filtrer la carte par ville",
    ["Toutes"] + sorted(df_agences["ville"].unique())
)

df_map = df_agences if ville_map == "Toutes" else df_agences[df_agences["ville"] == ville_map]
st.map(df_map[["latitude", "longitude"]])

st.divider()

# ======================== TABLE ========================

st.subheader("📋 Liste des agences")

st.dataframe(
    df_agences[["code_agence", "adresse_complete", "telephone", "site_web"]],
    use_container_width=True
)

# ======================== DETAILS ========================

st.subheader("🔍 Détails par ville")

ville_choice = st.selectbox(
    "Sélectionnez une ville",
    sorted(df_agences["ville"].unique())
)

for _, ag in df_agences[df_agences["ville"] == ville_choice].iterrows():
    with st.expander(f"🏢 Agence {ag['code_agence']}"):
        st.markdown(f"""
        **📍 Adresse** : {ag['adresse_complete']}  
        **📞 Téléphone** : {ag['telephone']}  
        **🌐 Site** : {ag['site_web']}
        """)

st.divider()

# ======================== DATA : CHAMBRES ========================

st.subheader("🛏️ Chambres disponibles")

sql_chambres = """
SELECT
    CodR AS code,
    Floor AS etage,
    SurfaceArea AS superficie,
    Type AS type
FROM ROOM
LIMIT 5
"""

df_chambres = run_query(sql_chambres)

images = {
    "Simple": "assets/simple.jpg",
    "Double": "assets/double.jpg",
    "Triple": "assets/triple.jpg",
    "Suite": "assets/suite.jpg"
}

for index, row in df_chambres.iterrows():
    col_info, col_img = st.columns([2, 1])

    with col_info:
        st.markdown(f"""
        ### 🛎️ Chambre {row['code']}
        - **Étage** : {row['etage']}
        - **Superficie** : {row['superficie']} m²
        - **Type** : {row['type']}
        """)
        st.button("Réserver", key=f"res_{index}")

    with col_img:
        st.image(
            images.get(row["type"], images["Simple"]),
            use_container_width=True
        )

    st.divider()

# ======================== FOOTER ========================

st.markdown("""
<div style="text-align:center; opacity:0.7; margin-top:40px">
    Application de gestion hôtelière • Streamlit Professional UI
</div>
""", unsafe_allow_html=True)
