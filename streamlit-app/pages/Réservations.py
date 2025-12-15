import streamlit as st
import pandas as pd
import datetime as dt
import calendar
import altair as alt  # <-- NOUVEAU: Importer Altair
from utils import get_db_connection

# st.set_page_config doit toujours être au début
st.set_page_config(page_title="Réservations - Complet", layout="wide")

st.markdown("""
<style>

/* ===============================
    FOND GLOBAL (GRIS TRÈS CLAIR)
================================ */
.stApp {
    background-color: #F5F5F5; /* Gris très clair (Palette: #F5F5F5) */
    color: #4B164C; 
    font-family: 'Poppins', sans-serif;
}

/* ===============================
    SIDEBAR (VIOLET TRÈS FONCÉ)
================================ */
section[data-testid="stSidebar"] {
    background-color: #4B164C; /* Violet foncé de la palette */
    color: white;
    box-shadow: 4px 0 10px rgba(75, 22, 76, 0.4);
}

section[data-testid="stSidebar"] * {
    color: #F5F5F5;
    font-weight: 500;
}

/* ===============================
    HEADER / EN-TÊTE PRINCIPAL (BANDE INDIGO)
================================ */
/* Utilisation de la nouvelle couleur #92487A pour la bande d'en-tête */
[data-testid="stVerticalBlock"] > div:first-child > div:first-child {
    background-color: #92487A; /* NOUVELLE COULEUR D'ACCENTUATION */
    padding: 25px 30px;
    margin-bottom: 25px;
    border-radius: 0 0 15px 15px; 
    box-shadow: 0 3px 10px rgba(146, 72, 122, 0.6);
}

/* ===============================
    TITRES
================================ */
h1, h2, h3 {
    color: #4B164C; /* Violet très foncé pour la lisibilité */
    font-weight: 700;
}

[data-testid="stVerticalBlock"] > div:first-child > div:first-child h1 {
    color: white; /* Texte blanc sur le fond Indigo */
    font-size: 2.2em;
}

/* ===============================
    CONTENU PRINCIPAL / CARTES D'ANALYSE
================================ */
.block-container {
    background-color: #F8E7F6; /* Blanc cassé de la palette */
    border-radius: 12px; 
    padding: 2.5rem;
    margin-top: 2rem;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    border-left: 5px solid #92487A; /* Ligne d'accentuation en Indigo */
}

/* ===============================
    NAVIGATION SIDEBAR 
================================ */

/* Lien actif (page sélectionnée) */
.st-emotion-cache-1y4v0h-anchor[aria-current="page"] {
    background-color: #92487A; /* Indigo pour l'élément actif */
    color: white !important; /* Texte blanc sur l'élément sombre */
    font-weight: 700;
    border-radius: 6px;
}

/* ===============================
    INPUTS / FILTRES (CLARTÉ)
================================ */
input, select, textarea {
    background-color: #FFFFFF !important; 
    color: #4B164C !important;
    border-radius: 6px !important;
    border: 1px solid #92487A !important; /* Bordure Indigo */
}

/* Focus */
input:focus, select:focus, textarea:focus {
    border-color: #4B164C !important; 
    box-shadow: 0 0 0 3px rgba(75, 22, 76, 0.3) !important;
}

/* ===============================
    BOUTONS
================================ */
.stButton > button {
    background-color: #4B164C; /* Violet très foncé pour l'action */
    color: white; 
    border-radius: 30px;
    padding: 10px 25px;
    font-weight: 700;
    border: none;
    transition: background-color 0.3s ease, transform 0.3s;
}

.stButton > button:hover {
    background-color: #6A226B; 
    transform: translateY(-2px);
}

/* ===============================
    TABLEAUX DE DONNÉES (DATAFRAME)
================================ */
.stDataFrame {
    background-color: #FFFFFF; 
    border-radius: 8px;
    padding: 15px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* En-têtes du tableau */
.stDataFrame > div > div > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) {
    color: #4B164C !important; 
    font-weight: 700;
    border-bottom: 2px solid #92487A; /* Bordure Indigo sous les en-têtes */
}

/* ===============================
    TABS
================================ */
button[data-baseweb="tab"] {
    background-color: #F8E7F6; 
    color: #4B164C;
    border-radius: 8px 8px 0 0;
    font-weight: 600;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background-color: #92487A; /* Indigo pour l'onglet actif */
    color: white; 
    font-weight: 700;
}

</style>

<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)
# --- 0. CONFIGURATION ---

st.title("📊 Gestion, Filtrage et Analyse des Réservations")


# --- 1. FONCTIONS D'ANALYSE (Exigences du Professeur) ---

@st.cache_data
def get_monthly_average_cost(_conn):
    """Calcule le coût journalier moyen par mois pour le graphique."""
    query = """
    SELECT
        DATE_FORMAT(date_debut, '%Y-%m') AS AnneeMois,
        AVG(prix / DATEDIFF(date_fin, date_debut)) AS Cout_Journalier_Moyen
    FROM RESERVATION
    GROUP BY AnneeMois
    ORDER BY AnneeMois;
    """
    df = pd.read_sql(query, _conn)
    # Convertit le mois numérique en nom de mois (Ex: 01 -> January)
    df['Mois'] = df['AnneeMois'].apply(lambda x: calendar.month_name[int(x.split('-')[1])].capitalize())
    return df


@st.cache_data
def get_highest_cost_room_per_month(_conn):
    """Trouve la chambre avec le coût journalier moyen le plus élevé pour chaque mois, avec le type (Suite ou Simple)."""
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
    df = df.rename(columns={'Cout_Moyen_Chambre': 'Coût Journalier Moyen (Max)'})
    return df


# --- 2. BARRE LATÉRALE ET FILTRES (Aucun changement ici) ---

st.sidebar.header("Options de Filtrage")

# Initial connection to get filter data
conn = get_db_connection()
agences_list = ['Toutes']
if conn:
    try:
        # Récupération de la liste des agences pour le filtre
        df_agences = pd.read_sql("SELECT Cod_A FROM AGENCE", conn)
        agences_list = ['Toutes'] + df_agences['Cod_A'].astype(str).tolist()
    except Exception as e:
        st.sidebar.error(f"Erreur chargement agences: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

# Filtres
agence_filtre = st.sidebar.selectbox("Filtrer par Code Agence :", agences_list)
date_debut_filtre = st.sidebar.date_input("Date de début (après ou égale à) :", value=None)
date_fin_filtre = st.sidebar.date_input("Date de fin (avant ou égale à) :", value=None)

# --- 3. SECTION 1 : AFFICHAGE DÉTAILLÉ (FILTRÉ) (Aucun changement ici) ---

st.header("1. Détails des Réservations Filtrées")

conn = get_db_connection()
if conn is not None:
    try:
        # Requête pour l'affichage détaillé, affectée par les filtres
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

        # Application des filtres
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
            # Correction: utiliser les bons noms de colonnes (prix, cout_journalier)
            if 'prix' in df_detail.columns:
                df_detail['prix'] = df_detail['prix'].apply(lambda x: f"{x:.2f} DH")
            if 'Coût_Journalier' in df_detail.columns:
                df_detail['Coût_Journalier'] = df_detail['Coût_Journalier'].apply(lambda x: f"{x:.2f} DH")
            st.dataframe(df_detail, use_container_width=True)
        else:
            st.info("Aucune réservation ne correspond aux filtres sélectionnés.")

    except Exception as e:
        st.error(f"Erreur lors de la requête détaillée : {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

st.divider()

# --- 4. SECTION 2 : ANALYSES DES TENDANCES (Exigences du Professeur) ---
st.header("2. Analyse des Tendances Mensuelles")
st.caption("Ces analyses sont des exigences du projet et ne sont pas affectées par les filtres de la barre latérale.")

# Création des onglets pour la navigation (2.1 et 2.2)
tab_graphique, tab_max_cout = st.tabs(
    ["📉 2.1. Évolution du Coût Journalier Moyen", "🏆 2.2. Chambre la Plus Chère par Mois"])

# --- 2.1. Onglet Graphique d'évolution (MODIFIÉ) ---
with tab_graphique:
    conn_tab = get_db_connection()
    if conn_tab is not None:
        try:
            df_monthly_avg = get_monthly_average_cost(conn_tab)
            if not df_monthly_avg.empty:

                # --- CONSTRUCTION DU GRAPHIQUE ALTAIR PERSONNALISÉ ---

                # Définition du graphique en ligne
                chart = alt.Chart(df_monthly_avg).mark_line().encode(
                    # Axe X: Noms des mois avec rotation de 45 degrés
                    x=alt.X('Mois', sort='ascending', axis=alt.Axis(
                        title='Mois',
                        labelAngle=45  # Rotation de 45 degrés pour les étiquettes
                    )),
                    # Axe Y: Coût journalier moyen avec titre incluant "DH"
                    y=alt.Y('Cout_Journalier_Moyen', axis=alt.Axis(
                        title='Coût Journalier Moyen (DH)'  # Titre d'axe personnalisé
                    )),
                    tooltip=['Mois', alt.Tooltip('Cout_Journalier_Moyen', format='.2f')]
                ).properties(
                    title='Évolution du Coût Journalier Moyen par Mois'
                ).interactive()  # Permet le zoom et le déplacement

                st.altair_chart(chart, use_container_width=True)  # Utiliser st.altair_chart
                # --- FIN DE LA CONSTRUCTION DU GRAPHIQUE ---

                st.caption("Graphique linéaire illustrant l'évolution du coût journalier moyen au fil des mois.")
            else:
                st.info("Aucune donnée pour l'analyse mensuelle du coût moyen.")
        except Exception as e:
            st.error(f"Erreur lors de la requête du graphique : {e}")
        finally:
            if conn_tab and conn_tab.is_connected():
                conn_tab.close()

# --- 2.2. Onglet Tableau de la chambre la plus chère (Aucun changement ici) ---
with tab_max_cout:
    conn_tab = get_db_connection()
    if conn_tab is not None:
        try:
            df_highest_cost = get_highest_cost_room_per_month(conn_tab)
            if not df_highest_cost.empty:
                df_highest_cost['Coût Journalier Moyen (Max)'] = df_highest_cost['Coût Journalier Moyen (Max)'].apply(
                    lambda x: f"{x:.2f} DH")

                df_display = df_highest_cost[
                    ['Mois', 'Code_Chambre', 'Type_Chambre', 'Étage', 'Superficie', 'Coût Journalier Moyen (Max)']]

                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True
                )
                st.caption(
                    "Tableau affichant le code, l'étage, la superficie et le type de chambre ayant le coût journalier moyen le plus élevé pour chaque mois.")
            else:
                st.info("Aucune donnée pour la table des chambres les plus chères.")
        except Exception as e:
            st.error(f"Erreur lors de la requête Max Coût : {e}")
        finally:
            if conn_tab and conn_tab.is_connected():
                conn_tab.close()

st.divider()

# --- 5. SECTION 3 : HISTORIQUE AGRÉGÉ (FILTRÉ) (Aucun changement ici) ---
st.header("3. Chiffre d'Affaires et Historique Agrégé")
st.caption("Cette agrégation est affectée par les filtres de la barre latérale.")

conn = get_db_connection()
if conn is not None:
    try:
        # Requête pour l'agrégation, affectée par les filtres
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

        # Application des filtres de la barre latérale
        if agence_filtre != "Toutes":
            query4 += " AND A.Cod_A = %s"
            params4.append(agence_filtre)
        if date_debut_filtre:
            query4 += " AND R.date_debut >= %s"
            params4.append(date_debut_filtre)
        if date_fin_filtre:
            query4 += " AND R.date_fin <= %s"
            params4.append(date_fin_filtre)

        query4 += " GROUP BY R.CHAMBRE_Cod_C, A.Cod_A"
        query4 += " ORDER BY Chiffre_Affaires_Total DESC"

        df_agg = pd.read_sql(query4, conn, params=params4)

        if not df_agg.empty:
            df_agg['Chiffre_Affaires_Total'] = df_agg['Chiffre_Affaires_Total'].apply(lambda x: f"{x:.2f} DH")
            st.dataframe(df_agg, use_container_width=True)
        else:
            st.info("Aucune donnée historique ne correspond aux filtres.")

    except Exception as e:
        st.error(f"Erreur lors de la requête agrégée : {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()