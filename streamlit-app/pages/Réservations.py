
import streamlit as st
import pandas as pd
import calendar
import altair as alt
from utils import get_db_connection

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
# ================= RESERVATION MANAGEMENT =================
st.subheader("🛠️ Gestion rapide des réservations")

tab_add, tab_update, tab_delete = st.tabs(
    ["➕ Ajouter", "✏️ Modifier", "🗑️ Supprimer"]
)

# ---------- ADD RESERVATION ----------
with tab_add:
    st.markdown("### 🛏️ Ajouter une réservation (chambres libres)")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        new_start = st.date_input("Date début", key="add_start")
    with c2:
        new_end = st.date_input("Date fin", key="add_end")
    with c3:
        new_agency = st.selectbox(
            "Agence",
            run_query(sql_agences)["CodA"].tolist(),
            key="add_agency"
        )
    with c4:
        new_cost = st.number_input("Coût total (DH)", min_value=0.0, step=50.0)

    if new_start and new_end and new_start < new_end:
        free_rooms = run_query(
            """
            SELECT R.CodR, R.Type, R.Floor, R.SurfaceArea
            FROM ROOM R
            WHERE R.CodR NOT IN (
                SELECT ROOM_CodR
                FROM BOOKING
                WHERE NOT (
                    EndDate <= %s OR StartDate >= %s
                )
            )
            ORDER BY R.Type, R.Floor
            """,
            [new_start, new_end]
        )

        if free_rooms.empty:
            st.warning("❌ Aucune chambre disponible pour cette période")
        else:
            room_choice = st.selectbox(
                "Chambre disponible",
                free_rooms["CodR"].tolist(),
                format_func=lambda x: f"Chambre {x}"
            )

            if st.button("✅ Créer la réservation", use_container_width=True):
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO BOOKING
                    (ROOM_CodR, StartDate, EndDate, Cost, TRAVEL_AGENCY_CodA)
                    VALUES (%s,%s,%s,%s,%s)
                    """,
                    (room_choice, new_start, new_end, new_cost, new_agency)
                )
                conn.commit()
                conn.close()
                st.success("🎉 Réservation ajoutée avec succès")
                st.rerun()

# ---------- UPDATE RESERVATION ----------
with tab_update:
    st.markdown("### ✏️ Modifier une réservation")

    bookings = run_query("""
        SELECT ROOM_CodR, StartDate, EndDate, Cost, TRAVEL_AGENCY_CodA
        FROM BOOKING
        ORDER BY StartDate DESC
    """)

    if bookings.empty:
        st.info("Aucune réservation à modifier")
    else:
        idx = st.selectbox(
            "Sélectionner une réservation",
            bookings.index,
            format_func=lambda i:
                f"Chambre {bookings.loc[i,'ROOM_CodR']} | {bookings.loc[i,'StartDate']}"
        )

        row = bookings.loc[idx]

        u1, u2, u3 = st.columns(3)
        with u1:
            upd_start = st.date_input(
                "Nouveau début",
                pd.to_datetime(row["StartDate"]),
                key="upd_start"
            )
        with u2:
            upd_end = st.date_input(
                "Nouvelle fin",
                pd.to_datetime(row["EndDate"]),
                key="upd_end"
            )
        with u3:
            upd_cost = st.number_input(
                "Nouveau coût",
                value=float(row["Cost"]),
                step=50.0
            )

        upd_agency = st.selectbox(
            "Agence",
            run_query(sql_agences)["CodA"].tolist(),
            index=run_query(sql_agences)["CodA"].tolist().index(
                row["TRAVEL_AGENCY_CodA"]
            )
        )

        if st.button("💾 Mettre à jour", use_container_width=True):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE BOOKING
                SET StartDate=%s, EndDate=%s, Cost=%s, TRAVEL_AGENCY_CodA=%s
                WHERE ROOM_CodR=%s AND StartDate=%s
                """,
                (
                    upd_start, upd_end, upd_cost, upd_agency,
                    row["ROOM_CodR"], row["StartDate"]
                )
            )
            conn.commit()
            conn.close()
            st.success("✔️ Réservation mise à jour")
            st.rerun()

# ---------- DELETE RESERVATION ----------
with tab_delete:
    st.markdown("### 🗑️ Supprimer une réservation")

    del_idx = st.selectbox(
        "Réservation à supprimer",
        bookings.index,
        format_func=lambda i:
            f"Chambre {bookings.loc[i,'ROOM_CodR']} | {bookings.loc[i,'StartDate']}"
    )

    del_row = bookings.loc[del_idx]

    if st.button("❌ Supprimer définitivement", type="primary", use_container_width=True):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            DELETE FROM BOOKING
            WHERE ROOM_CodR=%s AND StartDate=%s
            """,
            (del_row["ROOM_CodR"], del_row["StartDate"])
        )
        conn.commit()
        conn.close()
        st.success("🧹 Réservation supprimée")
        st.rerun()

st.divider()


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
