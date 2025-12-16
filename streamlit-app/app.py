import streamlit as st
from db import run_query # Assurez-vous que cette fonction est bien définie
from datetime import datetime

# --- Configuration de la Page ---
st.set_page_config(page_title="Dashboard Hôtelier - Grand Hôtel Chain", page_icon="🏨", layout="wide")

# Liste des membres du groupe (à personnaliser)
TEAM_MEMBERS = [
    {"name": "Membre 1", "role": "Chef de Projet"},
    {"name": "Membre 2", "role": "Développeur Back-end"},
    {"name": "Membre 3", "role": "Développeur Front-end"},
    {"name": "Membre 4", "role": "Spécialiste Base de Données"},
    {"name": "Membre 5", "role": "Designer UX/UI"},
    {"name": "Membre 6", "role": "Testeur QA"},
    {"name": "Membre 7", "role": "Rédacteur Technique"},
]

# --- CSS Injected: Thème Professionnel et Esthétique ---
# Load global CSS from styles/main.css
with open("styles/main.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inject the same theme as Agences.py for sidebar/gradient consistency
with open("theme.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Fonction Utile pour la Navigation ---
def go_to(page):
    """Gère la navigation entre les pages (compatible avec la structure pages/)"""
    try:
        st.switch_page(page)
    except Exception:
        st.session_state["_page"] = page
        st.experimental_rerun()

# --- 1 & 2. Hero Section + Introduction (Avec Image de Fond étendue) ---
st.markdown(f"""
<div class='hero-section-bg'>
    <div class='hero-header'>
        <h1 class='hero-title'>
            GRAND HOTEL CHAIN
        </h1>
        <p class='hero-subtitle'>
            Système de Gestion des Réservations Hôtelières
        </p>
    </div>
    <div style='display: flex; justify-content: center;'>
        <div style='max-width: 800px; width: 100%;'>
            <p class='intro-text'>
                Bienvenue sur votre tableau de bord central. Accédez en un coup d'œil aux indicateurs clés de performance <br>
                et utilisez les raccourcis ci-dessous pour une navigation rapide.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 3. Boutons d'Accès Rapide ---
col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("📅 Gérer les Réservations", key="quick_btn_reservations_1", use_container_width=True, help="Accéder au module Réservations"):
        go_to("pages/Réservations.py")

with col_btn2:
    if st.button("🛏️ Inventaire des Chambres", key="quick_btn_rooms_2", use_container_width=True, help="Accéder au module Chambres"):
        go_to("pages/Chambres.py")
        
with col_btn3:
    if st.button("🏢 Partenaires & Agences", key="quick_btn_agencies_3", use_container_width=True, help="Accéder au module Agences"):
        go_to("pages/Agences.py")

# --- 4. Quick Stats Section (Cartes d'Aperçu Rapide) ---
st.markdown("<h2 class='section-header'>Indicateurs Clés de Performance</h2>", unsafe_allow_html=True)

try:
    # Récupérer les statistiques
    total_rooms_df = run_query("SELECT COUNT(*) as count FROM ROOM;")
    total_reservations_df = run_query("SELECT COUNT(*) as count FROM BOOKING;")
    total_agencies_df = run_query("SELECT COUNT(*) as count FROM TRAVEL_AGENCY;")
    
    total_rooms = total_rooms_df.iloc[0]['count'] if not total_rooms_df.empty else 0
    total_reservations = total_reservations_df.iloc[0]['count'] if not total_reservations_df.empty else 0
    total_agencies = total_agencies_df.iloc[0]['count'] if not total_agencies_df.empty else 0

    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        if st.button(" ", key="card1_rooms", help="Voir les chambres", use_container_width=True): go_to("pages/Chambres.py")
        st.markdown(f"""
        <div class='stat-card card-rooms' style='margin-top:-3.2rem;'>
            <div class='card-icon'>🛏️</div>
            <div class='card-count'>{total_rooms}</div>
            <div class='card-label' style='color: white;'>Chambres Totales</div>
        </div>""", unsafe_allow_html=True)
        
    with col_stat2:
        if st.button(" ", key="card2_reservations", help="Voir les réservations", use_container_width=True): go_to("pages/Réservations.py")
        st.markdown(f"""
        <div class='stat-card card-reservations' style='margin-top:-3.2rem;'>
            <div class='card-icon'>📅</div>
            <div class='card-count'>{total_reservations}</div>
            <div class='card-label' style='color: white;'>Réservations Actives</div>
        </div>""", unsafe_allow_html=True)
        
    with col_stat3:
        if st.button(" ", key="card3_agencies", help="Voir les agences", use_container_width=True): go_to("pages/Agences.py")
        st.markdown(f"""
        <div class='stat-card card-agencies' style='margin-top:-3.2rem;'>
            <div class='card-icon'>🤝</div>
            <div class='card-count'>{total_agencies}</div>
            <div class='card-label' style='color: white;'>Agences Partenaires</div>
        </div>""", unsafe_allow_html=True)

except Exception as e:
    st.error("Erreur de connexion à la base de données. Vérifiez `db.py` et la disponibilité du service.")
    st.code(str(e))

st.markdown("<br><br>", unsafe_allow_html=True)

# =======================================================
# --- NOUVELLE SECTION : MEMBRES DE L'ÉQUIPE (GROUPE 9) ---
# =======================================================

st.markdown("<h2 class='section-header' style='margin-top: 1rem;'>Notre Équipe Projet 🚀</h2>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; margin-bottom: 2rem;'><p style='font-size: 1.2rem; color: #586069;'>Fièrement présenté par le <strong class='group-number'>Groupe 9</strong></p></div>", unsafe_allow_html=True)


# On utilise 4 colonnes pour la première ligne (4 membres) et 3 colonnes pour la seconde (3 membres)
# 7 membres: 4 | 3

# Ligne 1: 4 membres
cols_row1 = st.columns(4)

for i in range(4):
    member = TEAM_MEMBERS[i]
    with cols_row1[i]:
        st.markdown(f"""
        <div class='team-card'>
            <div style='font-size: 2rem; margin-bottom: 0.5rem;'>👤</div>
            <div class='member-name'>{member['name']}</div>
            <div class='member-role'>{member['role']}</div>
        </div>
        """, unsafe_allow_html=True)

# Ligne 2: 3 membres (centrés)
col_spacer1, col_center1, col_center2, col_center3, col_spacer2 = st.columns([0.5, 1, 1, 1, 0.5])

# On itère sur les 3 membres restants (index 4, 5, 6)
center_cols = [col_center1, col_center2, col_center3]
for i in range(4, 7):
    member = TEAM_MEMBERS[i]
    with center_cols[i - 4]: # i - 4 = 0, 1, 2
        st.markdown(f"""
        <div class='team-card'>
            <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🧑‍💻</div>
            <div class='member-name'>{member['name']}</div>
            <div class='member-role'>{member['role']}</div>
        </div>
        """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)

# --- 5. Section Statut de la Base de Données ---
with st.expander("🔌 Statut du Système & Diagnostic", expanded=False):
    st.markdown("### Vérification du Statut")
    try:
        run_query("SELECT 1 AS ok;")
        col_a, col_b = st.columns([1, 3])
        with col_a:
            st.success("✅ Service Opérationnel")
        with col_b:
            st.info(f"Connecté à MySQL • Dernière vérification : **{datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}**")
        st.markdown("<small>Le système est prêt. Veuillez utiliser le menu de navigation pour les opérations courantes.</small>", unsafe_allow_html=True)
    except Exception as e:
        st.error("❌ ERREUR CRITIQUE DE CONNEXION")
        st.warning("Impossible de se connecter à la base de données. Veuillez contacter l'administrateur système.")
        st.code(str(e), language="text")

# --- 6. Footer ---
st.markdown("""
<div class='footer'>
    <p>
        Développé par <strong>Groupe 9</strong> • Projet de Gestion Hôtelière
    </p>
    <p style='margin-top: 0.25rem;'>
        Système de Réservation Multi-Agences pour Chaîne Hôtelière • &copy; {year}
    </p>
</div>
""".format(year=datetime.now().year), unsafe_allow_html=True)