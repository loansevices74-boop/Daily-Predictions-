import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('ODD-API-KEY')
BASE_URL = "https://v3.football.api-sports.io"

# League IDs (expand as needed)
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
    # Add more leagues as needed
}

CONFIDENCE_THRESHOLD = 0.70