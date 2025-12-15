import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import get_db_connection
from datetime import datetime

st.set_page_config(page_title="Consultation & Filtrage des Chambres", page_icon="🔍", layout="wide")
st.title("🔍 Consultation & Filtrage des Chambres - Chainhotel")


# ========== FONCTIONS UTILES ==========
def execute_query(query, params=None):
    """Exécute une requête SQL avec paramètres"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    return None


def get_chambres_with_details():
    """Récupère toutes les chambres avec leurs détails (correspondance stricte au schéma SQL)"""
    query = """
    SELECT 
        c.Cod_C,
        c.surface,
        c.numero_etage,
        CASE 
            WHEN s.CHAMBRE_Cod_C IS NOT NULL THEN 'Oui'
            ELSE 'Non'
        END as est_suite,
        GROUP_CONCAT(DISTINCT he.EQUIPEMENT_equipement SEPARATOR ', ') as equipements,
        GROUP_CONCAT(DISTINCT hed.ESPACES_DISPO_Espaces_Dispo SEPARATOR ', ') as espaces_dispo,
        COUNT(DISTINCT r.date_debut) as nombre_reservations,
        COALESCE(SUM(r.prix), 0) as revenu_total
    FROM CHAMBRE c
    LEFT JOIN SUITE s ON c.Cod_C = s.CHAMBRE_Cod_C
    LEFT JOIN HAS_EQUIPEMENT he ON c.Cod_C = he.CHAMBRE_Cod_C
    LEFT JOIN HAS_ESPACES_DISPO hed ON s.CHAMBRE_Cod_C = hed.SUITE_CHAMBRE_Cod_C
    LEFT JOIN RESERVATION r ON c.Cod_C = r.CHAMBRE_Cod_C
    GROUP BY c.Cod_C, c.surface, c.numero_etage, s.CHAMBRE_Cod_C
    ORDER BY c.Cod_C
    """
    return execute_query(query)


# ========== SIDEBAR : FILTRES ==========
st.sidebar.header("🎯 Filtres de Recherche")

# Filtre par type de chambre
filter_type = st.sidebar.multiselect(
    "Type de chambre:",
    ["Standard", "Suite"],
    default=["Standard", "Suite"]
)

# Filtre par étage
etages = execute_query("SELECT DISTINCT numero_etage FROM CHAMBRE ORDER BY numero_etage")
etage_options = [str(e['numero_etage']) for e in etages] if etages else []
filter_etage = st.sidebar.multiselect(
    "Étage:",
    etage_options,
    default=etage_options
)

# Filtre par surface
st.sidebar.subheader("Surface (m²)")
col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    min_surface = st.number_input("Min", value=15.0, min_value=0.0, step=1.0)
with col_s2:
    max_surface = st.number_input("Max", value=50.0, min_value=0.0, step=1.0)

# Filtre par équipements
equipements = execute_query("SELECT DISTINCT EQUIPEMENT_equipement FROM HAS_EQUIPEMENT ORDER BY EQUIPEMENT_equipement")
equip_options = [e['EQUIPEMENT_equipement'] for e in equipements] if equipements else []
filter_equip = st.sidebar.multiselect(
    "Équipements:",
    equip_options
)

# Filtre par disponibilité (réservations)
filter_dispo = st.sidebar.radio(
    "Disponibilité:",
    ["Toutes", "Disponibles", "Réservées"]
)

# Bouton pour appliquer/réinitialiser
col_btn1, col_btn2 = st.sidebar.columns(2)
with col_btn1:
    apply_filters = st.button("🔍 Appliquer filtres", type="primary")
with col_btn2:
    reset_filters = st.button("🔄 Réinitialiser")

# ========== SECTION PRINCIPALE ==========
st.header("📋 Liste des Chambres")

# Récupérer les données
chambres_data = get_chambres_with_details()

if chambres_data:
    df = pd.DataFrame(chambres_data)

    # CORRECTION : Convertir les colonnes numériques
    df['surface'] = pd.to_numeric(df['surface'], errors='coerce')
    df['revenu_total'] = pd.to_numeric(df['revenu_total'], errors='coerce')
    df['nombre_reservations'] = pd.to_numeric(df['nombre_reservations'], errors='coerce')

    # Appliquer les filtres
    if apply_filters or not reset_filters:
        # Filtre type (Standard/Suite)
        if "Suite" in filter_type and "Standard" not in filter_type:
            df = df[df['est_suite'] == 'Oui']
        elif "Standard" in filter_type and "Suite" not in filter_type:
            df = df[df['est_suite'] == 'Non']

        # Filtre étage
        if filter_etage:
            df = df[df['numero_etage'].astype(str).isin(filter_etage)]

        # Filtre surface
        df = df[(df['surface'] >= min_surface) & (df['surface'] <= max_surface)]

        # Filtre équipements
        if filter_equip:
            mask = df['equipements'].apply(
                lambda x: any(equip in str(x) for equip in filter_equip) if pd.notna(x) else False
            )
            df = df[mask]

        # Filtre disponibilité
        if filter_dispo == "Disponibles":
            df = df[df['nombre_reservations'] == 0]
        elif filter_dispo == "Réservées":
            df = df[df['nombre_reservations'] > 0]

    # Afficher les métriques
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Chambres trouvées", len(df))
    with col2:
        suites = len(df[df['est_suite'] == 'Oui'])
        st.metric("Suites", suites)
    with col3:
        avg_surface = df['surface'].mean()
        st.metric("Surface moyenne", f"{avg_surface:.1f} m²")
    with col4:
        total_revenue = df['revenu_total'].sum()
        st.metric("Revenu total", f"{total_revenue:,.0f} DH")

    # Afficher le tableau avec options d'affichage
    st.subheader("📊 Tableau des chambres")

    # Options d'affichage
    show_details = st.checkbox("Afficher tous les détails", value=True)

    if show_details:
        columns_to_show = ['Cod_C', 'surface', 'numero_etage', 'est_suite',
                           'equipements', 'espaces_dispo', 'nombre_reservations', 'revenu_total']
        column_names = ['Code', 'Surface (m²)', 'Étage', 'Suite',
                        'Équipements', 'Espaces', 'Réservations', 'Revenu (DH)']
    else:
        columns_to_show = ['Cod_C', 'surface', 'numero_etage', 'est_suite', 'nombre_reservations']
        column_names = ['Code', 'Surface (m²)', 'Étage', 'Suite', 'Réservations']

    # Créer un DataFrame pour l'affichage
    display_df = df[columns_to_show].copy()
    display_df.columns = column_names

    # CORRECTION : Utiliser 'use_container_width' au lieu de 'width'
    st.dataframe(
        display_df,
        column_config={
            "Surface (m²)": st.column_config.NumberColumn(format="%.1f"),
            "Revenu (DH)": st.column_config.NumberColumn(format="%.0f DH"),
            "Réservations": st.column_config.NumberColumn(format="%d")
        },
        hide_index=True,
        use_container_width=True,  # Use the correct argument for Streamlit
        height=400
    )

    # Options d'export
    st.download_button(
        label="📥 Exporter en CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"chambres_filtrees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

    # ========== VISUALISATIONS ==========
    st.header("📈 Visualisations")

    tab1, tab2, tab3 = st.tabs(["Répartition par étage", "Surface vs Réservations", "Top chambres par revenu"])

    with tab1:
        # Graphique par étage
        etage_counts = df.groupby('numero_etage').size()
        fig1, ax1 = plt.subplots()
        ax1.bar(etage_counts.index.astype(str), etage_counts.values)
        ax1.set_xlabel('Étage')
        ax1.set_ylabel('Nombre de chambres')
        ax1.set_title('Répartition des chambres par étage')
        st.pyplot(fig1)

    with tab2:
        # Nuage de points surface vs réservations
        fig2, ax2 = plt.subplots()
        scatter = ax2.scatter(df['surface'], df['nombre_reservations'],
                              c=df['numero_etage'], cmap='viridis', alpha=0.6, s=100)
        ax2.set_xlabel('Surface (m²)')
        ax2.set_ylabel('Nombre de réservations')
        ax2.set_title('Surface vs Réservations')
        plt.colorbar(scatter, label='Étage')
        st.pyplot(fig2)

    with tab3:
        # Top chambres par revenu - CORRECTION
        if not df.empty and 'revenu_total' in df.columns:
            # Assurer que revenu_total est numérique
            df_top = df.copy()
            df_top['revenu_total'] = pd.to_numeric(df_top['revenu_total'], errors='coerce')
            df_top = df_top.dropna(subset=['revenu_total'])

            if not df_top.empty:
                top_chambres = df_top.nlargest(5, 'revenu_total')[['Cod_C', 'revenu_total']]
                fig3, ax3 = plt.subplots()
                ax3.barh(top_chambres['Cod_C'].astype(str), top_chambres['revenu_total'])
                ax3.set_xlabel('Revenu total (DH)')
                ax3.set_title('Top 5 chambres par revenu')
                st.pyplot(fig3)
            else:
                st.info("Aucune donnée de revenu disponible")
        else:
            st.info("Données de revenu non disponibles")

    # ========== DÉTAILS PAR CHAMBRE ==========
    st.header("🔍 Détail par chambre")

    chambre_codes = df['Cod_C'].tolist()
    selected_chambre = st.selectbox("Sélectionner une chambre pour détails:", chambre_codes)

    if selected_chambre:
        # Récupérer les détails complets de la chambre
        query_details = """
        SELECT 
            c.Cod_C,
            c.surface,
            c.numero_etage,
            CASE WHEN s.CHAMBRE_Cod_C IS NOT NULL THEN 'Oui' ELSE 'Non' END as est_suite,
            GROUP_CONCAT(DISTINCT he.EQUIPEMENT_equipement) as liste_equipements,
            GROUP_CONCAT(DISTINCT hed.ESPACES_DISPO_Espaces_Dispo) as liste_espaces,
            (SELECT COUNT(*) FROM RESERVATION r WHERE r.CHAMBRE_Cod_C = c.Cod_C) as nb_reservations
        FROM CHAMBRE c
        LEFT JOIN SUITE s ON c.Cod_C = s.CHAMBRE_Cod_C
        LEFT JOIN HAS_EQUIPEMENT he ON c.Cod_C = he.CHAMBRE_Cod_C
        LEFT JOIN HAS_ESPACES_DISPO hed ON s.CHAMBRE_Cod_C = hed.SUITE_CHAMBRE_Cod_C
        WHERE c.Cod_C = %s
        GROUP BY c.Cod_C, c.surface, c.numero_etage, s.CHAMBRE_Cod_C
        """

        details = execute_query(query_details, (selected_chambre,))

        if details:
            detail = details[0]

            col_d1, col_d2 = st.columns(2)

            with col_d1:
                st.subheader(f"Chambre {detail['Cod_C']}")
                st.write(f"**Surface:** {detail['surface']} m²")
                st.write(f"**Étage:** {detail['numero_etage']}")
                st.write(f"**Suite:** {detail['est_suite']}")
                st.write(f"**Réservations:** {detail['nb_reservations']}")

            with col_d2:
                if detail['liste_equipements']:
                    st.subheader("Équipements")
                    for equip in detail['liste_equipements'].split(','):
                        st.write(f"• {equip.strip()}")

                if detail['liste_espaces'] and detail['est_suite'] == 'Oui':
                    st.subheader("Espaces (suite)")
                    for espace in detail['liste_espaces'].split(','):
                        st.write(f"• {espace.strip()}")

            # Réservations de cette chambre
            query_reservations = """
            SELECT 
                r.date_debut,
                r.date_fin,
                r.prix,
                a.Cod_A,
                a.site_web
            FROM RESERVATION r
            JOIN AGENCE a ON r.AGENCE_Cod_A = a.Cod_A
            WHERE r.CHAMBRE_Cod_C = %s
            ORDER BY r.date_debut DESC
            """

            reservations = execute_query(query_reservations, (selected_chambre,))

            if reservations:
                st.subheader("📅 Historique des réservations")
                res_df = pd.DataFrame(reservations)
                st.dataframe(res_df, hide_index=True, use_container_width=True)  # CORRECTION

else:
    st.warning("Aucune donnée de chambre trouvée dans la base de données.")

# ========== FOOTER ==========
st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Fonctionnalités :**
    - 🔍 Filtrage avancé des chambres
    - 📊 Visualisations interactives
    - 📥 Export des données
    - 🔍 Détails par chambre

    **Base :** Chainhotel
    **Tables utilisées :** CHAMBRE, SUITE, HAS_EQUIPEMENT, HAS_ESPACES_DISPO, RESERVATION
    """
)