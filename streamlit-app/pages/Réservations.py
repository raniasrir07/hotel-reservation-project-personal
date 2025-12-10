# Fichier: streamlit_app/pages/3_Réservations.py

import streamlit as st
from utils import fetch_data_as_df
import plotly.express as px

st.set_page_config(page_title="Analyse des Réservations", layout="wide")
st.title("📈 Analyse des Coûts des Réservations")

# --- 1. Requête pour l'analyse mensuelle (Coût journalier moyen) ---
# On utilise MONTHNAME pour l'affichage et MONTH pour le tri
sql_monthly_analysis = """
SELECT
    -- Calcul du coût journalier moyen pour chaque réservation
    YEAR(R.date_debut) AS Annee,
    MONTH(R.date_debut) AS NumMois,
    MONTHNAME(R.date_debut) AS Mois,
    AVG(R.prix_journalier) AS Cout_Moyen_Journalier
FROM
    RESERVATION R
GROUP BY
    Annee, NumMois, Mois
ORDER BY
    Annee ASC, NumMois ASC;
"""
df_monthly_avg = fetch_data_as_df(sql_monthly_analysis)


# --- 2. Graphique Linéaire de l'Évolution du Coût ---
st.subheader("Évolution du Coût Journalier Moyen des Réservations")

if not df_monthly_avg.empty:
    # Trier le DataFrame pour que le graphique soit dans le bon ordre
    df_monthly_avg = df_monthly_avg.sort_values(by=['Annee', 'NumMois'])
    
    # Créer une colonne pour l'axe X : Mois et Année combinés
    df_monthly_avg['Période'] = df_monthly_avg['Mois'] + ' ' + df_monthly_avg['Annee'].astype(str)

    fig = px.line(
        df_monthly_avg,
        x='Période',
        y='Cout_Moyen_Journalier',
        text='Cout_Moyen_Journalier', # Afficher les valeurs sur les points
        title='Coût Journalier Moyen par Mois de Réservation',
        labels={'Cout_Moyen_Journalier': 'Coût (€/jour)', 'Période': 'Mois'}
    )
    fig.update_traces(texttemplate='%{text:.2f}€', textposition="bottom right")
    fig.update_layout(hovermode="x unified")
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Aucune donnée de réservation trouvée pour l'analyse des coûts.")


st.markdown("---")

# --- 3. Requête pour la Chambre la plus chère par mois ---
st.subheader("Chambre la plus chère (en moyenne) par Mois")

# Requête complexe utilisant des CTE (Common Table Expressions) ou des sous-requêtes
sql_max_daily_cost = """
WITH ChambreMoyenne AS (
    -- 1. Calcul du coût journalier moyen pour chaque chambre dans chaque mois
    SELECT
        YEAR(R.date_debut) AS Annee,
        MONTH(R.date_debut) AS NumMois,
        MONTHNAME(R.date_debut) AS Mois,
        R.numeroChambre,
        AVG(R.prix_journalier) AS AvgDailyCost
    FROM RESERVATION R
    GROUP BY Annee, NumMois, Mois, R.numeroChambre
),
MaxCostMois AS (
    -- 2. Trouver le coût maximal pour chaque mois
    SELECT
        Annee,
        NumMois,
        MAX(AvgDailyCost) AS MaxAvgCost
    FROM ChambreMoyenne
    GROUP BY Annee, NumMois
)
-- 3. Joindre les informations pour trouver la chambre correspondante
SELECT
    CMM.Annee,
    CMM.NumMois,
    CM.Mois,
    C.numeroChambre AS Code,
    C.etage AS Étage,
    C.superficie_m2 AS Superficie_m2,
    C.typeChambre AS Type,
    ROUND(CMM.MaxAvgCost, 2) AS Coût_Journalier_Moyen_Max
FROM MaxCostMois CMM
JOIN ChambreMoyenne CM
    ON CMM.Annee = CM.Annee AND CMM.NumMois = CM.NumMois AND CMM.MaxAvgCost = CM.AvgDailyCost
JOIN CHAMBRE C
    ON CM.numeroChambre = C.numeroChambre
ORDER BY
    CMM.Annee ASC, CMM.NumMois ASC;
"""

df_max_cost = fetch_data_as_df(sql_max_daily_cost)

if not df_max_cost.empty:
    # Renommer la colonne des mois pour l'affichage
    df_display = df_max_cost.rename(columns={'Mois': 'Mois de Réservation'})
    st.dataframe(df_display[['Mois de Réservation', 'Code', 'Étage', 'Superficie_m2', 'Type', 'Coût_Journalier_Moyen_Max']], use_container_width=True)

    st.markdown("""
    > **Note :** La chambre listée est celle qui avait le coût journalier moyen le plus élevé
    > parmi toutes les réservations durant le mois spécifié.
    """)
else:
    st.info("Aucune donnée pour déterminer la chambre la plus chère par mois.")