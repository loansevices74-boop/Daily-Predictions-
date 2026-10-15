import streamlit as st
import os

# Try every possible key name - this will work no matter what
API_KEY = (
    st.secrets.get("ODD_API_KEY") or
    st.secrets.get("ODD-API-KEY") or
    st.secrets.get("odd_api_key") or
    os.getenv("ODD_API_KEY") or
    os.getenv("ODD-API-KEY") or
    ""
)

BASE_URL = "https://v3.football.api-sports.io"

LEAGUES = {
    'Premier League': 39,
    'La Liga': 140,
    'Serie A': 135,
    'Bundesliga': 78,
    'Ligue 1': 61,
    'Championship': 40,
    'Champions League': 2,
    'Europa League': 3,
    'Conference League': 848,
}

CONFIDENCE_THRESHOLD = 0.70