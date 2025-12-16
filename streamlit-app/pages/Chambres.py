import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import get_db_connection

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Chambres – ChainHotel",
    page_icon="🛏️",
    layout="wide"
)

st.markdown('<style>' + open('theme.css').read() + '</style>', unsafe_allow_html=True)

# ================= TITLE =================
st.title("🛏️ Gestion & Consultation des Chambres")
st.caption("Recherche intelligente, affichage premium et analyse visuelle")
st.divider()

# ================= DB HELPER (MOVED UP) =================
def run_query(query, params=None):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(query, params or ())
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

# ================= SQL (MOVED UP) =================
query = """
SELECT
    r.CodR,
    r.Floor,
    r.SurfaceArea,
    r.Type,
    GROUP_CONCAT(DISTINCT ha.AMENITIES_Amenity) AS amenities,
    GROUP_CONCAT(DISTINCT hs.SPACES_Space) AS spaces
FROM ROOM r
LEFT JOIN HAS_AMENITIES ha ON r.CodR = ha.ROOM_CodR
LEFT JOIN HAS_SPACES hs ON r.CodR = hs.ROOM_CodR
GROUP BY r.CodR, r.Floor, r.SurfaceArea, r.Type
"""
df = pd.DataFrame(run_query(query))

# ================= STATISTIQUES (MOVED) =================
st.subheader("📊 Statistiques clés")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Chambres trouvées", len(df))
with c2:
    st.metric("Surface moyenne", f"{df['SurfaceArea'].mean():.1f} m²")
with c3:
    st.metric("Suites", len(df[df["Type"] == "suite"]))
with c4:
    st.metric("Étage max", df["Floor"].max())

# ================= SIDEBAR FILTERS =================
st.sidebar.title("🎯 Filtres")

type_filter = st.sidebar.radio(
    "Type de chambre",
    ["toutes", "single", "double", "triple", "suite"]
)

amenities = run_query(
    "SELECT DISTINCT AMENITIES_Amenity FROM HAS_AMENITIES ORDER BY AMENITIES_Amenity"
)
amenities_list = [a["AMENITIES_Amenity"] for a in amenities]

selected_amenities = st.sidebar.multiselect(
    "Options disponibles",
    amenities_list
)

kitchen_only = st.sidebar.checkbox("🍳 Avec cuisine")

st.sidebar.divider()
st.sidebar.caption("Les résultats se mettent à jour automatiquement")

# ================= APPLY FILTERS =================
if type_filter != "toutes":
    df = df[df["Type"] == type_filter]

if selected_amenities:
    df = df[df["amenities"].fillna("").apply(
        lambda x: all(a in x for a in selected_amenities)
    )]

if kitchen_only:
    df = df[df["spaces"].fillna("").str.contains("kitchen")]

# ================= TABLE =================
st.subheader("📋 Chambres disponibles")

table_df = df[["CodR", "Floor", "SurfaceArea", "Type"]].copy()
table_df.columns = ["Code", "Étage", "Superficie (m²)", "Type"]

st.dataframe(table_df, hide_index=True, use_container_width=True)

# ================= CARTES CHAMBRES =================
st.divider()
st.subheader("✨ Aperçu premium des chambres")

images = {
    "single": "assets/simple.jpg",
    "double": "assets/double.jpg",
    "triple": "assets/triple.jpg",
    "suite": "assets/suite.jpg"
}

for _, row in df.head(5).iterrows():
    col_text, col_img = st.columns([2, 1])

    with col_text:
        st.markdown(f"""
        ### 🛎️ Chambre {row['CodR']}
        - **Type** : {row['Type'].capitalize()}
        - **Étage** : {row['Floor']}
        - **Superficie** : {row['SurfaceArea']} m²
        - **Options** : {row['amenities'] or "Aucune"}
        """)

    with col_img:
        st.image(images.get(row["Type"]), use_container_width=True)

    st.divider()

# ================= VISUALISATIONS =================
st.divider()
st.subheader("📈 Analyse visuelle")

tab1, tab2, tab3 = st.tabs(
    ["🏢 Par type", "🏬 Par étage", "📐 Surfaces"]
)

with tab1:
    type_counts = df["Type"].value_counts()
    fig, ax = plt.subplots()
    ax.bar(type_counts.index, type_counts.values)
    ax.set_title("Répartition par type")
    ax.set_xlabel("Type")
    ax.set_ylabel("Nombre")
    st.pyplot(fig)

with tab2:
    floor_counts = df["Floor"].value_counts().sort_index()
    fig, ax = plt.subplots()
    ax.bar(floor_counts.index.astype(str), floor_counts.values)
    ax.set_title("Répartition par étage")
    ax.set_xlabel("Étage")
    ax.set_ylabel("Nombre")
    st.pyplot(fig)

with tab3:
    fig, ax = plt.subplots()
    ax.hist(df["SurfaceArea"], bins=8)
    ax.set_title("Distribution des surfaces")
    ax.set_xlabel("Surface (m²)")
    ax.set_ylabel("Nombre")
    st.pyplot(fig)

# ================= FOOTER =================
st.markdown(
    "<div style='text-align:center; opacity:0.6; margin-top:40px'>"
    "Module Chambres – ChainHotel • Streamlit Ultra Premium"
    "</div>",
    unsafe_allow_html=True
)
