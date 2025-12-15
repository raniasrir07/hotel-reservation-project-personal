import streamlit as st
from db import run_query

st.set_page_config(page_title="Hotel Reservation", page_icon="🏨", layout="wide")

# Inject global theme CSS
st.markdown('<style>' + open('theme.css').read() + '</style>', unsafe_allow_html=True)

st.title("🏨 Hotel Reservation Project")
st.write("Bienvenue dans l'application.")

# Optionnel: statut DB
with st.expander("🔌 Statut connexion base de données"):
    try:
        df = run_query("SELECT 1 AS ok;")
        st.success("Connexion MySQL OK ✅")
    except Exception as e:
        st.error("Connexion MySQL KO ❌")
        st.code(str(e))
