import streamlit as st
import os

# API KEY FIX: Put your actual key inside the quotes below
API_KEY = "547904d85d424ac91ad9a2071e98c79e" 

BASE_URL = "https://v3.football.api-sports.io"

# COMPLETE LEAGUE LIST (API-Football IDs)
LEAGUES = {
    # --- TOP 5 LEAGUES ---
    'Premier League': 39,
    'La Liga': 140,
    'Serie A': 135,
    'Bundesliga': 78,
    'Ligue 1': 61,
    
    # --- 2ND DIVISIONS ---
    'Championship (ENG)': 40,
    'La Liga 2 (ESP)': 141,
    'Serie B (ITA)': 136,
    'Bundesliga 2 (GER)': 79,
    'Ligue 2 (FRA)': 62,
    
    # --- OTHER TOP EUROPEAN LEAGUES ---
    'Eredivisie (NED)': 88,
    'Primeira Liga (POR)': 94,
    'Scottish Premiership': 179,
    'Belgian Pro League': 144,
    'Austrian Bundesliga': 218,
    'Swiss Super League': 207,
    'Danish Superliga': 119,
    'Norwegian Eliteserien': 103,
    'Swedish Allsvenskan': 113,
    'Turkish Super Lig': 203,
    'Greek Super League': 197,
    'Russian Premier': 235,
    'Ukrainian Premier': 333,
    'Czech First League': 345,
    'Romanian Liga 1': 283,
    'Croatian HNL': 210,
    'Serbian SuperLiga': 286,
    
    # --- AMERICAS ---
    'MLS (USA)': 253,
    'Brasileirão Serie A (BRA)': 71,
    'Liga Profesional (ARG)': 128,
    
    # --- UEFA & EUROPEAN TOURNAMENTS ---
    'UEFA Champions League': 2,
    'UEFA Europa League': 3,
    'UEFA Conference League': 848,
    'UEFA Super Cup': 531,
    'UEFA Nations League': 5,
    
    # --- MAJOR LEAGUE CUPS / DOMESTIC CUPS ---
    'FA Cup (ENG)': 45,
    'EFL Cup (ENG)': 48,
    'Copa del Rey (ESP)': 143,
    'Coppa Italia (ITA)': 137,
    'DFB Pokal (GER)': 81,
    'Coupe de France (FRA)': 66,
    'KNVB Beker (NED)': 89,
    'Taça de Portugal (POR)': 96,
    'Scottish FA Cup': 181,
    'Copa do Brasil (BRA)': 73,
}

CONFIDENCE_THRESHOLD = 0.70