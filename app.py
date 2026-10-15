import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

# ==========================================
# PASTE YOUR ACTUAL API KEY INSIDE THE QUOTES BELOW
# ==========================================
API_KEY = "547904d85d424ac91ad9a2071e98c79e" 
# ==========================================

BASE_URL = "https://v3.football.api-sports.io"

# Check if key is valid
if not API_KEY or API_KEY == "547904d85d424ac91ad9a2071e98c79e":
    st.error("⚠️ You forgot to paste your API key in the code! Open app.py and add it.")
    st.stop()

st.set_page_config(page_title="Football Predictor", layout="wide")
st.title("🏆 Football Prediction System")
st.markdown("### Daily High-Confidence Picks (>70%)")

# Success message
st.sidebar.success(f"✅ API Key Connected")

LEAGUES = {
    'Premier League': 39, 'La Liga': 140, 'Serie A': 135, 'Bundesliga': 78, 'Ligue 1': 61,
    'Championship': 40, 'Champions League': 2, 'Europa League': 3, 'Conference League': 848,
    'Eredivisie': 88, 'Primeira Liga': 94, 'Scottish Premiership': 179, 'MLS': 253,
    'Brasileirão': 71, 'Liga Profesional': 128, 'Turkish Super Lig': 203
}

def get_fixtures(date_str):
    url = f"{BASE_URL}/fixtures"
    params = {'date': date_str, 'timezone': 'UTC'}
    headers = {'x-apisports-key': API_KEY}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        return response.json().get('response', [])
    except:
        return []

def get_odds(fixture_id):
    url = f"{BASE_URL}/odds"
    params = {'fixture': fixture_id}
    headers = {'x-apisports-key': API_KEY}
    try:
        time.sleep(1) # Prevent throttling
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json().get('response', [])
        return data[0] if data else None
    except:
        return None

def calculate_confidence(odds_data):
    if not odds_data: return None, None
    try:
        bookmakers = odds_data.get('bookmakers', [])
        if not bookmakers: return None, None
        bets = bookmakers[0].get('bets', [])
        match_1x2 = next((b for b in bets if b.get('name') == 'Match Winner'), None)
        if not match_1x2: return None, None
        
        values = match_1x2.get('values', [])
        odds_dict = {v['value']: float(v['odd']) for v in values}
        
        total_inverse = sum(1/o for o in odds_dict.values())
        probs = {k: (1/v) / total_inverse for k, v in odds_dict.items()}
        
        best_outcome = max(probs, key=probs.get)
        return best_outcome, probs[best_outcome]
    except:
        return None, None

# Date selection
today = datetime.now()
selected_date = st.sidebar.date_input("Select Date", today)
date_str = selected_date.strftime('%Y-%m-%d')

if st.sidebar.button("🔄 Generate Predictions", type="primary"):
    with st.spinner(f"Fetching fixtures for {date_str}..."):
        fixtures = get_fixtures(date_str)
        
        if not fixtures:
            st.warning(f"⚠️ No fixtures found for {date_str}")
            st.stop()
        
        league_ids = set(LEAGUES.values())
        league_fixtures = [f for f in fixtures if f.get('league', {}).get('id') in league_ids]
        
        all_predictions = []
        
        for fixture in league_fixtures:
            try:
                fixture_id = fixture['fixture']['id']
                odds_data = get_odds(fixture_id)
                
                if not odds_data: continue
                
                outcome, confidence = calculate_confidence(odds_data)
                
                if outcome and confidence and confidence >= 0.70:
                    # Get odds for the predicted outcome
                    bookmakers = odds_data.get('bookmakers', [])
                    bets = bookmakers[0].get('bets', [])
                    match_1x2 = next((b for b in bets if b.get('name') == 'Match Winner'), None)
                    odds_val = next((v['odd'] for v in match_1x2['values'] if v['value'] == outcome), 0)
                    
                    all_predictions.append({
                        'league': fixture.get('league', {}).get('name', ''),
                        'home_team': fixture['teams']['home']['name'],
                        'away_team': fixture['teams']['away']['name'],
                        'outcome': outcome,
                        'confidence': confidence,
                        'odds': float(odds_val),
                        'kickoff': fixture['fixture']['date'][11:16]
                    })
            except:
                continue
        
        st.success(f"✅ Found {len(all_predictions)} high-confidence predictions!")
        
        if not all_predictions:
            st.info("No predictions met the 70% threshold today.")
            st.stop()
        
        all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        folder1 = [p for p in all_predictions if p['outcome'] == 'Home'][:3]
        folder2 = [p for p in all_predictions if p['outcome'] == 'Draw'][:3]
        folder3 = [p for p in all_predictions if p['outcome'] == 'Away'][:3]
        folder4 = sorted(all_predictions, key=lambda x: x['odds'], reverse=True)[:3]
        
        tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home Wins", "🤝 Draws", "✈️ Away Wins", "💎 High Value"])
        
        for tab, folder, label in zip([tab1, tab2, tab3, tab4], [folder1, folder2, folder3, folder4], ["Home Wins", "Draws", "Away Wins", "High Value"]):
            with tab:
                if folder:
                    df = pd.DataFrame([{
                        'League': p['league'],
                        'Match': f"{p['home_team']} vs {p['away_team']}",
                        'Pick': p['outcome'],
                        'Confidence': f"{p['confidence']:.1%}",
                        'Odds': f"{p['odds']:.2f}",
                        'Time': p['kickoff']
                    } for p in folder])
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info(f"No {label} predictions")

st.markdown("---")
st.markdown(f"⏰ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")