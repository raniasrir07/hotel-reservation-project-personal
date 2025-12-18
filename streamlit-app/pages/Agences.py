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

# Hide default Streamlit sidebar and nav
with open(os.path.join(os.path.dirname(__file__), '..', 'styles', 'main.css')) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Import custom CSS for Agences page
with open(os.path.join(os.path.dirname(__file__), '..', 'styles', 'agences.css')) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Custom sidebar (copied from app.py)
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="hotel-logo">🏨</div>
        <div class="hotel-name">Grand Hotel Chain</div>
        <div class="hotel-role">Hotel Management System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 🧭 Navigation")
    if st.button("📊 Dashboard", use_container_width=True):
        st.switch_page("app.py")

    if st.button("📅 Réservations", use_container_width=True):
        st.switch_page("pages/Réservations.py")

    if st.button("🛏️ Chambres", use_container_width=True):
        st.switch_page("pages/Chambres.py")

    if st.button("🤝 Agences", use_container_width=True):
        st.switch_page("pages/Agences.py")

    st.markdown("---")

    st.markdown("### ⚙️ Système")
    st.success("🟢 PMS en ligne")
    from datetime import datetime
    st.caption(f"Dernière synchronisation : {datetime.now().strftime('%H:%M:%S')}")

    st.markdown("""
    <div class="sidebar-footer">
        Groupe 9 • PMS Hôtelier
    </div>
    """, unsafe_allow_html=True)

theme_path = os.path.join(os.path.dirname(__file__), '..', 'theme.css')
with open(theme_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ======================== SQL QUERIES ========================
# Query for DATA : AGENCES section (distinct cities with agencies)
sql_villes = """
SELECT DISTINCT c.Name AS ville
FROM CITY c
JOIN TRAVEL_AGENCY a ON a.City_Address = c.Name
ORDER BY c.Name
"""

# Query for METRICS section (agency details with city info)
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

# Query for MAP section (agency details for map, all cities)
sql_agences_map_all = """
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

# Query for MAP section (agency details for map, filtered by city)
sql_agences_map_city = lambda ville_map: f"""
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
WHERE c.Name = '{ville_map}'
"""

# Query for TABLE section (agency list for table)
sql_agences_table = """
SELECT
    a.CodA AS code_agence,
    a.Tel AS telephone,
    a.WebSite AS site_web,
    CONCAT(a.Street_Address, ' ', a.Num_Address, ', ', c.Name) AS adresse_complete,
    c.Name AS ville
FROM TRAVEL_AGENCY a
JOIN CITY c ON a.City_Address = c.Name
"""

# Query for DETAILS section (agency details for selected city)
sql_agences_details = lambda ville_choice: f"""
SELECT
    a.CodA AS code_agence,
    a.Tel AS telephone,
    a.WebSite AS site_web,
    CONCAT(a.Street_Address, ' ', a.Num_Address, ', ', c.Name) AS adresse_complete
FROM TRAVEL_AGENCY a
JOIN CITY c ON a.City_Address = c.Name
WHERE c.Name = '{ville_choice}'
"""

# Query for DATA : CHAMBRES section (available rooms, limit 5)
sql_chambres = """
SELECT
    CodR AS code,
    Floor AS etage,
    SurfaceArea AS superficie,
    Type AS type
FROM ROOM
LIMIT 5
"""

# Query for AGENCY PERFORMANCE section (top 5 agencies by performance)
sql_agency_perf = """
SELECT
    a.CodA AS agence,
    COUNT(b.ROOM_CodR) AS total_reservations,
    SUM(b.Cost) AS chiffre_affaires
FROM TRAVEL_AGENCY a
LEFT JOIN BOOKING b ON a.CodA = b.TRAVEL_AGENCY_CodA
GROUP BY a.CodA
ORDER BY chiffre_affaires DESC
LIMIT 5
"""

# ======================== Header ========================

st.title("🏨 Tableau de bord – Gestion Hôtelière")
st.caption("Vue globale des agences & chambres disponibles")
st.divider()

# ======================== DATA : AGENCES ========================

df_villes = run_query(sql_villes)
villes_list = df_villes["ville"].tolist()

# ======================== METRICS ========================

df_agences = run_query(sql_agences)

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
    ["Toutes"] + villes_list
)

if ville_map == "Toutes":
    df_map = run_query(sql_agences_map_all)
else:
    df_map = run_query(sql_agences_map_city(ville_map))

st.map(df_map[["latitude", "longitude"]])

st.divider()

# ======================== TABLE ========================

st.subheader("📋 Liste des agences")

df_agences = run_query(sql_agences_table)

st.dataframe(
    df_agences[["code_agence", "adresse_complete", "telephone", "site_web"]],
    use_container_width=True
)

# ======================== DETAILS ========================

st.subheader("🔍 Détails par ville")

ville_choice = st.selectbox(
    "Sélectionnez une ville",
    villes_list
)

df_details = run_query(sql_agences_details(ville_choice))

for _, ag in df_details.iterrows():
    with st.expander(f"🏢 Agence {ag['code_agence']}"):
        st.markdown(f"""
        **📍 Adresse** : {ag['adresse_complete']}  
        **📞 Téléphone** : {ag['telephone']}  
        **🌐 Site** : {ag['site_web']}
        """)

st.divider()

# ======================== DATA : CHAMBRES ========================

st.subheader("🛏️ Chambres disponibles")

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

    with col_img:
        st.image(
            images.get(row["type"], images["Simple"]),
            use_container_width=True
        )

    st.divider()

# ======================== AGENCY PERFORMANCE ========================

st.subheader("🏆 Performance des agences")

df_perf = run_query(sql_agency_perf)

c1, c2 = st.columns(2)

with c1:
    st.markdown("#### 📅 Réservations par agence")
    st.dataframe(
        df_perf[["agence", "total_reservations"]],
        use_container_width=True
    )

with c2:
    st.markdown("#### 💰 Chiffre d’affaires (MAD)")
    st.dataframe(
        df_perf[["agence", "chiffre_affaires"]],
        use_container_width=True
    )

st.divider()

# ======================== FOOTER ========================

st.markdown("""
<div style="text-align:center; opacity:0.7; margin-top:40px">
    Application de gestion hôtelière • Streamlit Professional UI
</div>
""", unsafe_allow_html=True)
