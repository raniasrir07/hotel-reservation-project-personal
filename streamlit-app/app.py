import streamlit as st
from db import run_query
from datetime import datetime

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Grand Hotel Chain | Dashboard",
    page_icon="🏨",
    layout="wide"
)

# =====================================================
# LOAD CSS
# =====================================================
with open("styles/main.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =====================================================
# NAVIGATION HELPER
# =====================================================
def go_to(page):
    try:
        st.switch_page(page)
    except Exception:
        st.session_state["_page"] = page
        st.experimental_rerun()

# =====================================================
# SIDEBAR – HOTEL CONTROL PANEL
# =====================================================
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
        go_to("Home.py")

    if st.button("📅 Réservations", use_container_width=True):
        go_to("pages/Réservations.py")

    if st.button("🛏️ Chambres", use_container_width=True):
        go_to("pages/Chambres.py")

    if st.button("🤝 Agences", use_container_width=True):
        go_to("pages/Agences.py")

    st.markdown("---")

    st.markdown("### ⚙️ Système")
    st.success("🟢 PMS en ligne")
    st.caption(f"Dernière synchronisation : {datetime.now().strftime('%H:%M:%S')}")

    st.markdown("""
    <div class="sidebar-footer">
        Groupe 9 • PMS Hôtelier
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# HERO SECTION
# =====================================================
st.markdown("""
<div class='hero-section-bg'>
    <h1 class='hero-title'>GRAND HOTEL CHAIN</h1>
    <p class='hero-subtitle'>
        Property Management System • Réservations • Chambres • Partenaires
    </p>
    <p class='intro-text'>
        Supervisez l’activité hôtelière, optimisez l’occupation
        et gérez efficacement vos partenaires depuis une interface centralisée.
    </p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# QUICK ACTIONS
# =====================================================
st.markdown("<h2 class='section-header'>⚡ Actions Rapides</h2>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("➕ Nouvelle Réservation", use_container_width=True):
        go_to("pages/Réservations.py")

with c2:
    if st.button("🛏️ Gestion des Chambres", use_container_width=True):
        go_to("pages/Chambres.py")

with c3:
    if st.button("🤝 Ajouter une Agence", use_container_width=True):
        go_to("pages/Agences.py")

# =====================================================
# KPIs
# =====================================================
st.markdown("<h2 class='section-header'>📊 Indicateurs Clés</h2>", unsafe_allow_html=True)

try:
    # Query: total number of rooms
    total_rooms = run_query("SELECT COUNT(*) c FROM ROOM").iloc[0]["c"]
    # Query: total number of bookings
    total_res = run_query("SELECT COUNT(*) c FROM BOOKING").iloc[0]["c"]
    # Query: total number of agencies
    total_ag = run_query("SELECT COUNT(*) c FROM TRAVEL_AGENCY").iloc[0]["c"]

    k1, k2, k3 = st.columns(3)

    with k1:
        st.markdown(f"""
        <div class='stat-card card-rooms'>
            <div class='card-icon'>🛏️</div>
            <div class='card-count'>{total_rooms}</div>
            <div class='card-label'>Chambres Totales</div>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class='stat-card card-reservations'>
            <div class='card-icon'>📅</div>
            <div class='card-count'>{total_res}</div>
            <div class='card-label'>Réservations</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class='stat-card card-agencies'>
            <div class='card-icon'>🤝</div>
            <div class='card-count'>{total_ag}</div>
            <div class='card-label'>Agences Partenaires</div>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error("Erreur de connexion à la base de données")
    st.code(str(e))


# TEAM MEMBERS
# =====================================================
st.markdown("<h2 class='section-header'>👥 Équipe du Projet</h2>", unsafe_allow_html=True)

# Carousel for team members
import streamlit.components.v1 as components

carousel_html = '''
<style>
.carousel-container {
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
  padding-bottom: 10px;
  margin-bottom: 2rem;
}
.carousel-team-card {
  display: inline-block;
  background: linear-gradient(135deg, #1e3c72, #2a5298);
  border-radius: 16px;
  padding: 2rem 1.5rem;
  text-align: center;
  color: white;
  box-shadow: 0 10px 28px rgba(0,0,0,0.25);
  transition: transform 0.3s ease;
  min-width: 220px;
  max-width: 260px;
  margin-right: 1.5rem;
  vertical-align: top;
}
.carousel-team-card:hover {
  transform: translateY(-6px);
}
.carousel-team-avatar {
  font-size: 2.5rem;
  margin-bottom: 0.8rem;
}
.carousel-team-name {
  font-weight: 700;
  font-size: 1.05rem;
}
.carousel-team-role {
  font-size: 0.9rem;
  opacity: 0.85;
  margin-top: 0.3rem;
}
</style>
<div class="carousel-container">
  <div class="carousel-team-card">
    <div class="carousel-team-avatar">👤</div>
    <div class="carousel-team-name">Bilal SAHILI</div>
  </div>
  <div class="carousel-team-card">
    <div class="carousel-team-avatar">👤</div>
    <div class="carousel-team-name">Rania SRIR</div>
  </div>
  <div class="carousel-team-card">
    <div class="carousel-team-avatar">👤</div>
    <div class="carousel-team-name">Oussama MOTASSIM</div>
  </div>
  <div class="carousel-team-card">
    <div class="carousel-team-avatar">👤</div>
    <div class="carousel-team-name">Bouchra WISSAM</div>
  </div>
  <div class="carousel-team-card">
    <div class="carousel-team-avatar">👤</div>
    <div class="carousel-team-name">Chaimae HAZZOT</div>
  </div>
  <div class="carousel-team-card">
    <div class="carousel-team-avatar">👤</div>
    <div class="carousel-team-name">Adam FISSAL</div>
  </div>
  <div class="carousel-team-card">
    <div class="carousel-team-avatar">👤</div>
    <div class="carousel-team-name">Fatima Ez-Zahrae ELARBAOUI</div>
  </div>
</div>
'''
st.markdown(carousel_html, unsafe_allow_html=True)

# =====================================================
# RECENT BOOKINGS
# =====================================================
st.markdown("<h2 class='section-header'>🕒 Réservations Récentes</h2>", unsafe_allow_html=True)

try:
    # Query: get 5 most recent bookings
    recent_bookings = run_query("""
        SELECT ROOM_CodR, StartDate, EndDate, Cost
        FROM BOOKING
        ORDER BY StartDate DESC
        LIMIT 5
    """)

    for _, row in recent_bookings.iterrows():
        st.markdown(f"""
        <div class="stat-card" style="margin-bottom:0.8rem;">
            🛏️ Chambre <strong>{row['ROOM_CodR']}</strong><br>
            📅 {row['StartDate']} → {row['EndDate']}<br>
            💰 {row['Cost']} MAD
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error("Erreur lors du chargement des réservations")
    st.code(str(e))
# =====================================================
# REVENUE SUMMARY
# =====================================================
st.markdown("<h2 class='section-header'>💰 Revenus Générés</h2>", unsafe_allow_html=True)

try:
    # Query: total revenue from bookings
    revenue = run_query("""
        SELECT SUM(Cost) total FROM BOOKING
    """).iloc[0]["total"]

    st.metric("💵 Revenu Total", f"{revenue:.0f} MAD")

except Exception as e:
    st.error("Erreur calcul revenus")
    st.code(str(e))

# =====================================================
# ROOM OCCUPANCY TODAY
# =====================================================
st.markdown("<h2 class='section-header'>🛏️ Occupation Aujourd’hui</h2>", unsafe_allow_html=True)

today = datetime.now().strftime("%Y-%m-%d")

try:
    # Query: number of rooms occupied today
    occupied_today = run_query(f"""
        SELECT COUNT(DISTINCT ROOM_CodR) c
        FROM BOOKING
        WHERE '{today}' BETWEEN StartDate AND EndDate
    """).iloc[0]["c"]

    # Query: total number of rooms (again)
    total_rooms = run_query("SELECT COUNT(*) c FROM ROOM").iloc[0]["c"]
    free_rooms = total_rooms - occupied_today

    o1, o2 = st.columns(2)
    o1.metric("❌ Chambres Occupées", occupied_today)
    o2.metric("✅ Chambres Libres", free_rooms)

except Exception as e:
    st.error("Erreur lors du calcul d’occupation")
    st.code(str(e))

# =====================================================
# SYSTEM ALERTS
# =====================================================
st.markdown("<h2 class='section-header'>🚨 Alertes Système</h2>", unsafe_allow_html=True)

alerts = []

if free_rooms == 0:
    alerts.append("⚠️ Hôtel complet aujourd’hui")

if revenue == 0:
    alerts.append("⚠️ Aucun revenu enregistré")

if total_ag == 0:
    alerts.append("⚠️ Aucune agence partenaire")

if alerts:
    for a in alerts:
        st.warning(a)
else:
    st.success("✅ Système stable — aucune alerte")

# =====================================================
# FOOTER
# =====================================================
st.markdown(f"""
<div class='footer'>
    <p><strong>Groupe 9</strong> • Projet de Gestion Hôtelière</p>
    <p>© {datetime.now().year} Grand Hotel Chain</p>
</div>
""", unsafe_allow_html=True)