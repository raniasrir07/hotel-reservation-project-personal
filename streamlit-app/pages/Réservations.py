import streamlit as st
import pandas as pd
import calendar
import altair as alt
from utils import get_db_connection

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Réservations – ChainHotel",
    page_icon="📊",
    layout="wide"
)

st.markdown('<style>' + open('theme.css').read() + '</style>', unsafe_allow_html=True)

# ================= TITLE =================
st.title("📊 Gestion & Analyse des Réservations")
st.caption("Suivi des performances, tendances tarifaires et réservations premium")
st.divider()

# ================= DB HELPERS =================
def run_query(query, params=None):
    conn = get_db_connection()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# ================= SIDEBAR =================
st.sidebar.title("🎛️ Filtres")

agences = run_query("SELECT CodA FROM TRAVEL_AGENCY ORDER BY CodA")
agence_list = ["Toutes"] + agences["CodA"].astype(str).tolist()

agence_filtre = st.sidebar.selectbox("Agence", agence_list)
date_debut = st.sidebar.date_input("Date début", value=None)
date_fin = st.sidebar.date_input("Date fin", value=None)

st.sidebar.divider()
st.sidebar.caption("Les données se mettent à jour automatiquement")

# ================= BASE QUERY =================
query = """
SELECT
    B.ROOM_CodR AS Code_Chambre,
    B.StartDate,
    B.EndDate,
    DATEDIFF(B.EndDate, B.StartDate) AS Duree,
    B.Cost,
    (B.Cost / DATEDIFF(B.EndDate, B.StartDate)) AS Cout_Journalier,
    T.CodA AS Code_Agence,
    R.Type AS Type_Chambre,
    R.Floor,
    R.SurfaceArea
FROM BOOKING B
JOIN TRAVEL_AGENCY T ON B.TRAVEL_AGENCY_CodA = T.CodA
JOIN ROOM R ON B.ROOM_CodR = R.CodR
WHERE 1=1
"""

params = []

if agence_filtre != "Toutes":
    query += " AND T.CodA = %s"
    params.append(agence_filtre)

if date_debut:
    query += " AND B.StartDate >= %s"
    params.append(date_debut)

if date_fin:
    query += " AND B.EndDate <= %s"
    params.append(date_fin)

query += " ORDER BY B.StartDate DESC"

df = run_query(query, params)

# ================= KPIs =================
st.subheader("📌 Indicateurs clés")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Réservations", len(df))

with c2:
    st.metric("Chiffre d'affaires", f"{df['Cost'].sum():,.0f} DH")

with c3:
    avg_duree = df['Duree'].mean()
    st.metric("Durée moyenne", f"{0 if pd.isna(avg_duree) else avg_duree:.1f} jours")

with c4:
    avg_cout_journalier = df['Cout_Journalier'].mean()
    st.metric("Coût moyen / jour", f"{0 if pd.isna(avg_cout_journalier) else avg_cout_journalier:.0f} DH")

# ================= TABLE =================
st.divider()
st.subheader("📋 Détails des réservations")

display_df = df.copy()
display_df["Cost"] = display_df["Cost"].map(lambda x: f"{x:.0f} DH")
display_df["Cout_Journalier"] = display_df["Cout_Journalier"].map(lambda x: f"{x:.0f} DH")

display_df = display_df.rename(columns={
    "StartDate": "Début",
    "EndDate": "Fin",
    "Duree": "Durée (jours)",
    "Cost": "Coût total",
    "Cout_Journalier": "Coût / jour",
    "Floor": "Étage",
    "SurfaceArea": "Superficie"
})

st.dataframe(display_df, use_container_width=True, height=420)

# ================= ANALYTICS =================
st.divider()
st.subheader("📈 Analyse avancée")

tab1, tab2, tab3 = st.tabs(
    ["📆 Évolution mensuelle", "💎 Chambres premium", "🏢 Performance par agence"]
)

# Prepare WHERE clause for analytics tabs
analytics_where = "WHERE 1=1"
analytics_params = []
if agence_filtre != "Toutes":
    analytics_where += " AND B.TRAVEL_AGENCY_CodA = %s"
    analytics_params.append(agence_filtre)
if date_debut:
    analytics_where += " AND B.StartDate >= %s"
    analytics_params.append(date_debut)
if date_fin:
    analytics_where += " AND B.EndDate <= %s"
    analytics_params.append(date_fin)

# ---------- TAB 1 ----------
with tab1:
    monthly_query = f"""
        SELECT
            DATE_FORMAT(B.StartDate, '%Y-%m') AS YM,
            AVG(B.Cost / DATEDIFF(B.EndDate, B.StartDate)) AS Cout_Journalier_Moyen
        FROM BOOKING B
        {analytics_where}
        GROUP BY YM
        ORDER BY YM
    """
    monthly = run_query(monthly_query, analytics_params)

    monthly["Mois"] = monthly["YM"].apply(
        lambda x: calendar.month_name[int(x.split("-")[1])].capitalize()
    )

    chart = alt.Chart(monthly).mark_line(
        point=True,
        strokeWidth=3
    ).encode(
        x=alt.X("Mois:N", title=""),
        y=alt.Y("Cout_Journalier_Moyen:Q", title="Coût journalier moyen (DH)"),
        tooltip=["Mois", alt.Tooltip("Cout_Journalier_Moyen:Q", format=".0f")]
    ).properties(height=350)

    st.altair_chart(chart, use_container_width=True)

# ---------- TAB 2 ----------
with tab2:
    premium_query = f"""
        SELECT
            DATE_FORMAT(B.StartDate, '%Y-%m') AS Mois,
            B.ROOM_CodR,
            R.Type,
            R.Floor,
            R.SurfaceArea,
            AVG(B.Cost / DATEDIFF(B.EndDate, B.StartDate)) AS Cout_Moyen
        FROM BOOKING B
        JOIN ROOM R ON B.ROOM_CodR = R.CodR
        {analytics_where}
        GROUP BY Mois, B.ROOM_CodR
        ORDER BY Cout_Moyen DESC
    """
    premium = run_query(premium_query, analytics_params)

    premium["Cout_Moyen"] = premium["Cout_Moyen"].map(lambda x: f"{x:.0f} DH")

    st.dataframe(
        premium.rename(columns={
            "ROOM_CodR": "Chambre",
            "Type": "Type",
            "Floor": "Étage",
            "SurfaceArea": "Superficie",
            "Cout_Moyen": "Coût journalier moyen"
        }),
        use_container_width=True,
        hide_index=True,
        height=380
    )

# ---------- TAB 3 ----------
with tab3:
    agency_perf_query = f"""
        SELECT
            T.CodA AS Agence,
            COUNT(*) AS Nb_Reservations,
            SUM(B.Cost) AS CA
        FROM BOOKING B
        JOIN TRAVEL_AGENCY T ON B.TRAVEL_AGENCY_CodA = T.CodA
        {analytics_where}
        GROUP BY T.CodA
        ORDER BY CA DESC
    """
    agency_perf = run_query(agency_perf_query, analytics_params)

    agency_perf["CA"] = agency_perf["CA"].map(lambda x: f"{x:.0f} DH")

    st.dataframe(
        agency_perf,
        use_container_width=True,
        hide_index=True,
        height=350
    )

# ================= FOOTER =================
st.markdown(
    "<div style='text-align:center; opacity:0.6; margin-top:40px'>"
    "Module Réservations – ChainHotel • Streamlit Ultra Premium"
    "</div>",
    unsafe_allow_html=True
)
