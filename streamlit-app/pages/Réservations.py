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

# Hide default Streamlit sidebar and nav
with open('styles/main.css') as f:
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

st.markdown('<style>' + open('theme.css').read() + '</style>', unsafe_allow_html=True)

# ================= TITLE =================
st.title("📊 Gestion & Analyse des Réservations")
st.caption("Suivi des performances, tendances tarifaires et réservations premium")
st.divider()

# ======================== SQL QUERIES ========================
# Query for SIDEBAR (agencies list)
sql_agences = """
SELECT CodA FROM TRAVEL_AGENCY ORDER BY CodA
"""

# Query for BASE QUERY (main reservations table, with filters)
def sql_reservations():
    return """
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

# Query for ANALYTICS TAB 1 (monthly evolution)
def sql_monthly(analytics_where):
    return f"""
        SELECT
            DATE_FORMAT(B.StartDate, '%Y-%m') AS YM,
            AVG(B.Cost / DATEDIFF(B.EndDate, B.StartDate)) AS Cout_Journalier_Moyen
        FROM BOOKING B
        {analytics_where}
        GROUP BY YM
        ORDER BY YM
    """

# Query for ANALYTICS TAB 2 (premium rooms)
def sql_premium(analytics_where):
    return f"""
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

# Query for ANALYTICS TAB 3 (agency performance)
def sql_agency_perf(analytics_where):
    return f"""
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

# ================= DB HELPERS =================
def run_query(query, params=None):
    conn = get_db_connection()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# ================= SIDEBAR =================
st.sidebar.title("🎛️ Filtres")

agences = run_query(sql_agences)
agence_list = ["Toutes"] + agences["CodA"].astype(str).tolist()

agence_filtre = st.sidebar.selectbox("Agence", agence_list)
date_debut = st.sidebar.date_input("Date début", value=None)
date_fin = st.sidebar.date_input("Date fin", value=None)

st.sidebar.divider()
st.sidebar.caption("Les données se mettent à jour automatiquement")

# ================= BASE QUERY =================
query = sql_reservations()
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
    monthly = run_query(sql_monthly(analytics_where), analytics_params)

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
    premium = run_query(sql_premium(analytics_where), analytics_params)

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
    agency_perf = run_query(sql_agency_perf(analytics_where), analytics_params)

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
