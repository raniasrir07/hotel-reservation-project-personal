import streamlit as st
# Inject global theme CSS
st.markdown('<style>' + open('theme.css').read() + '</style>', unsafe_allow_html=True)

