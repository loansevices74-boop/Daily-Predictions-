import streamlit as st
import os

# Try Streamlit secrets first, then env var
API_KEY = st.secrets.get("ODD_API_KEY", os.getenv("ODD_API_KEY", ""))
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
    'Eredivisie': 88,
    'Primeira Liga': 94,
    'Scottish Premiership': 179,
    'MLS': 253,
    'Brazilian Serie A': 71,
    'Argentine Liga': 128,
    'Turkish Super Lig': 203,
    'Russian Premier': 235,
    'Belgian Pro': 144,
    'Austrian Bundesliga': 218,
    'Swiss Super': 207,
    'Danish Superliga': 119,
    'Norwegian Eliteserien': 103,
    'Swedish Allsvenskan': 113,
}

CONFIDENCE_THRESHOLD = 0.70