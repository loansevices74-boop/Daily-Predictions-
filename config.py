"""Application configuration."""

from __future__ import annotations

import os

BASE_URL = os.getenv("FOOTBALL_API_BASE_URL", "https://v3.football.api-sports.io")
API_KEY_ENV = "FOOTBALL_API_KEY"
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.55"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
API_MIN_INTERVAL_SECONDS = float(os.getenv("API_MIN_INTERVAL_SECONDS", "0.25"))

LEAGUES = {
    "Premier League": 39, "La Liga": 140, "Serie A": 135,
    "Bundesliga": 78, "Ligue 1": 61, "Championship (ENG)": 40,
    "La Liga 2 (ESP)": 141, "Serie B (ITA)": 136,
    "Bundesliga 2 (GER)": 79, "Ligue 2 (FRA)": 62,
    "Eredivisie (NED)": 88, "Primeira Liga (POR)": 94,
    "Scottish Premiership": 179, "Belgian Pro League": 144,
    "Austrian Bundesliga": 218, "Swiss Super League": 207,
    "Danish Superliga": 119, "Turkish Super Lig": 203,
    "Greek Super League": 197, "MLS (USA)": 253,
    "Brasileirao Serie A (BRA)": 71, "Liga Profesional (ARG)": 128,
    "UEFA Champions League": 2, "UEFA Europa League": 3,
    "UEFA Conference League": 848, "FA Cup (ENG)": 45,
    "EFL Cup (ENG)": 48, "Copa del Rey (ESP)": 143,
    "Coppa Italia (ITA)": 137, "DFB Pokal (GER)": 81,
    "Coupe de France (FRA)": 66, "KNVB Beker (NED)": 89,
    "Taca de Portugal (POR)": 96, "Copa do Brasil (BRA)": 73,
}

TRACKED_LEAGUE_IDS = frozenset(LEAGUES.values())
