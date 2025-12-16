import streamlit as st
from db import run_query

st.title("🔌 Test Connexion MySQL")

try:
    df1 = run_query("SELECT 1 AS ok;")
    st.success("Connexion MySQL OK : ✅")
    st.dataframe(df1)

    st.subheader("Aperçu des villes")
    df2 = run_query("SELECT * FROM CITY;")
    st.dataframe(df2)

except Exception as e:
    st.error("Connexion MySQL échouée : ❌")
    st.code(str(e))
