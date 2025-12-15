import streamlit as st
import pandas as pd
import datetime as dt
import calendar
import altair as alt
from utils import get_db_connection

st.set_page_config(page_title="Réservations", layout="wide", page_icon="📊")

st.markdown('<style>' + open('theme.css').read() + '</style>', unsafe_allow_html=True)

# Simple title
st.title("📊 Réservations")
st.caption("Analyse des tendances et des coûts de réservation")

# --- FUNCTIONS ---

@st.cache_data
def get_monthly_average_cost(_conn):
    query = """
    SELECT
        DATE_FORMAT(date_debut, '%Y-%m') AS AnneeMois,
        AVG(prix / DATEDIFF(date_fin, date_debut)) AS Cout_Journalier_Moyen
    FROM RESERVATION
    GROUP BY AnneeMois
    ORDER BY AnneeMois;
    """
    df = pd.read_sql(query, _conn)
    df['Mois'] = df['AnneeMois'].apply(lambda x: calendar.month_name[int(x.split('-')[1])].capitalize())
    return df

@st.cache_data
def get_highest_cost_room_per_month(_conn):
    query = """
    WITH MonthlyAvgCost AS (
        SELECT
            r.CHAMBRE_Cod_C,
            DATE_FORMAT(r.date_debut, '%Y-%m') AS AnneeMois,
            (r.prix / DATEDIFF(r.date_fin, r.date_debut)) AS Cout_Journalier
        FROM RESERVATION r
    ),
    RankedRooms AS (
        SELECT
            m.AnneeMois,
            m.CHAMBRE_Cod_C,
            AVG(m.Cout_Journalier) AS Cout_Moyen_Chambre,
            ROW_NUMBER() OVER (PARTITION BY m.AnneeMois ORDER BY AVG(m.Cout_Journalier) DESC) AS rn
        FROM MonthlyAvgCost m
        GROUP BY m.AnneeMois, m.CHAMBRE_Cod_C
    )
    SELECT
        rr.AnneeMois,
        rr.CHAMBRE_Cod_C AS Code_Chambre,
        c.numero_etage AS Étage,
        c.Surface AS Superficie,
        rr.Cout_Moyen_Chambre,
        CASE 
            WHEN s.CHAMBRE_Cod_C IS NOT NULL THEN 'Suite' 
            ELSE 'Chambre Simple' 
        END AS Type_Chambre
    FROM RankedRooms rr
    JOIN CHAMBRE c ON rr.CHAMBRE_Cod_C = c.Cod_C
    LEFT JOIN SUITE s ON rr.CHAMBRE_Cod_C = s.CHAMBRE_Cod_C 
    WHERE rr.rn = 1
    ORDER BY rr.AnneeMois;
    """
    df = pd.read_sql(query, _conn)
    df['Mois'] = df['AnneeMois'].apply(lambda x: calendar.month_name[int(x.split('-')[1])].capitalize())
    df = df.rename(columns={'Cout_Moyen_Chambre': 'Coût Journalier Moyen'})
    return df

# --- SIDEBAR ---

st.sidebar.header("Filtres")

conn = get_db_connection()
agences_list = ['Toutes']
if conn:
    try:
        df_agences = pd.read_sql("SELECT Cod_A FROM AGENCE", conn)
        agences_list = ['Toutes'] + df_agences['Cod_A'].astype(str).tolist()
    except Exception as e:
        st.sidebar.error(f"Erreur: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

agence_filtre = st.sidebar.selectbox("Agence", agences_list)
date_debut_filtre = st.sidebar.date_input("Date début", value=None)
date_fin_filtre = st.sidebar.date_input("Date fin", value=None)

# --- SECTION 1: Details ---

st.header("Détails des réservations")

conn = get_db_connection()
if conn is not None:
    try:
        query1 = """
        SELECT
            R.CHAMBRE_Cod_C AS Code_Chambre,
            R.date_debut,
            R.date_fin,
            DATEDIFF(R.date_fin, R.date_debut) AS Durée_Jours,
            R.prix,
            (R.prix / DATEDIFF(R.date_fin, R.date_debut)) AS Coût_Journalier,
            A.Cod_A AS Code_Agence,
            A.Site_web AS Site_Agence
        FROM RESERVATION R
        INNER JOIN AGENCE A ON R.AGENCE_Cod_A = A.Cod_A
        WHERE 1=1
        """
        params1 = []

        if agence_filtre != "Toutes":
            query1 += " AND A.Cod_A = %s"
            params1.append(agence_filtre)
        if date_debut_filtre:
            query1 += " AND R.date_debut >= %s"
            params1.append(date_debut_filtre)
        if date_fin_filtre:
            query1 += " AND R.date_fin <= %s"
            params1.append(date_fin_filtre)

        query1 += " ORDER BY R.date_debut DESC"

        df_detail = pd.read_sql(query1, conn, params=params1)

        if not df_detail.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Réservations", len(df_detail))
            with col2:
                st.metric("Chiffre d'affaires", f"{df_detail['prix'].sum():,.0f} DH")
            with col3:
                st.metric("Durée moyenne", f"{df_detail['Durée_Jours'].mean():.1f} jours")
            with col4:
                st.metric("Coût moyen/jour", f"{df_detail['Coût_Journalier'].mean():.0f} DH")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if 'prix' in df_detail.columns:
                df_detail['prix'] = df_detail['prix'].apply(lambda x: f"{x:.2f} DH")
            if 'Coût_Journalier' in df_detail.columns:
                df_detail['Coût_Journalier'] = df_detail['Coût_Journalier'].apply(lambda x: f"{x:.2f} DH")
            
            st.dataframe(df_detail, use_container_width=True, height=400)
        else:
            st.info("Aucune réservation trouvée")

    except Exception as e:
        st.error(f"Erreur: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

st.divider()

# --- SECTION 2: Analysis ---

st.header("Analyse des tendances mensuelles")

tab1, tab2 = st.tabs(["Évolution des coûts", "Chambres premium"])

with tab1:
    conn_tab = get_db_connection()
    if conn_tab is not None:
        try:
            df_monthly_avg = get_monthly_average_cost(conn_tab)
            if not df_monthly_avg.empty:
                chart = alt.Chart(df_monthly_avg).mark_line(
                    point=True,
                    color='#92487A',
                    strokeWidth=2
                ).encode(
                    x=alt.X('Mois:N', sort=None, axis=alt.Axis(title='', labelAngle=-45)),
                    y=alt.Y('Cout_Journalier_Moyen:Q', axis=alt.Axis(title='Coût journalier moyen (DH)')),
                    tooltip=['Mois', alt.Tooltip('Cout_Journalier_Moyen:Q', format='.2f', title='Coût')]
                ).properties(
                    height=350
                ).configure_view(
                    strokeWidth=0
                ).configure_axis(
                    grid=True,
                    gridColor='#F5F5F5'
                )

                st.altair_chart(chart, use_container_width=True)
                st.caption("Évolution du coût journalier moyen par mois")
            else:
                st.info("Aucune donnée disponible")
        except Exception as e:
            st.error(f"Erreur: {e}")
        finally:
            if conn_tab and conn_tab.is_connected():
                conn_tab.close()

with tab2:
    conn_tab = get_db_connection()
    if conn_tab is not None:
        try:
            df_highest_cost = get_highest_cost_room_per_month(conn_tab)
            if not df_highest_cost.empty:
                df_highest_cost['Coût Journalier Moyen'] = df_highest_cost['Coût Journalier Moyen'].apply(
                    lambda x: f"{x:.2f} DH")

                df_display = df_highest_cost[
                    ['Mois', 'Code_Chambre', 'Type_Chambre', 'Étage', 'Superficie', 'Coût Journalier Moyen']]

                st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)
                st.caption("Chambre avec le coût journalier moyen le plus élevé par mois")
            else:
                st.info("Aucune donnée disponible")
        except Exception as e:
            st.error(f"Erreur: {e}")
        finally:
            if conn_tab and conn_tab.is_connected():
                conn_tab.close()

st.divider()

# --- SECTION 3: Aggregated ---

st.header("Historique agrégé")

conn = get_db_connection()
if conn is not None:
    try:
        query4 = """
        SELECT
            R.CHAMBRE_Cod_C AS Code_Chambre,
            A.Cod_A AS Code_Agence,
            COUNT(*) AS Nb_Reservations,
            SUM(R.prix) AS Chiffre_Affaires_Total
        FROM RESERVATION R
        INNER JOIN AGENCE A ON R.Agence_Cod_A = A.Cod_A
        WHERE 1=1
        """
        params4 = []

        if agence_filtre != "Toutes":
            query4 += " AND A.Cod_A = %s"
            params4.append(agence_filtre)
        if date_debut_filtre:
            query4 += " AND R.date_debut >= %s"
            params4.append(date_debut_filtre)
        if date_fin_filtre:
            query4 += " AND R.date_fin <= %s"
            params4.append(date_fin_filtre)

        query4 += " GROUP BY R.CHAMBRE_Cod_C, A.Cod_A ORDER BY Chiffre_Affaires_Total DESC"

        df_agg = pd.read_sql(query4, conn, params=params4)

        if not df_agg.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total réservations", f"{df_agg['Nb_Reservations'].sum():,}")
            with col2:
                st.metric("CA total", f"{df_agg['Chiffre_Affaires_Total'].sum():,.2f} DH")
            with col3:
                st.metric("Chambres actives", df_agg['Code_Chambre'].nunique())
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            df_agg['Chiffre_Affaires_Total'] = df_agg['Chiffre_Affaires_Total'].apply(lambda x: f"{x:.2f} DH")
            st.dataframe(df_agg, use_container_width=True, height=400)
        else:
            st.info("Aucune donnée disponible")

    except Exception as e:
        st.error(f"Erreur: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()