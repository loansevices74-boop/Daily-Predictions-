import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

# ==========================================
# 1. PASTE YOUR ACTUAL API KEY BELOW
# ==========================================
API_KEY = "547904d85d424ac91ad9a2071e98c79e" 
# ==========================================

BASE_URL = "https://v3.football.api-sports.io"

# Simple check to ensure a key was provided
if not API_KEY or API_KEY == "PASTE_YOUR_REAL_API_KEY_HERE":
    st.error("⚠️ Please open app.py and paste your actual API key on line 11.")
    st.stop()

st.set_page_config(page_title="Football Predictor", layout="wide")
st.title("🏆 Football Prediction System")
st.markdown("### Daily High-Confidence Picks (>70%)")
st.sidebar.success("✅ API Key Connected")

# ==========================================
# 2. COMPLETE LEAGUE LIST
# ==========================================
LEAGUES = {
    # Top 5 Leagues
    'Premier League': 39, 'La Liga': 140, 'Serie A': 135, 'Bundesliga': 78, 'Ligue 1': 61,
    # 2nd Divisions
    'Championship (ENG)': 40, 'La Liga 2 (ESP)': 141, 'Serie B (ITA)': 136, 'Bundesliga 2 (GER)': 79, 'Ligue 2 (FRA)': 62,
    # Other European Top Leagues
    'Eredivisie (NED)': 88, 'Primeira Liga (POR)': 94, 'Scottish Premiership': 179, 
    'Belgian Pro League': 144, 'Austrian Bundesliga': 218, 'Swiss Super League': 207, 
    'Danish Superliga': 119, 'Turkish Super Lig': 203, 'Greek Super League': 197,
    # Americas
    'MLS (USA)': 253, 'Brasileirão Serie A (BRA)': 71, 'Liga Profesional (ARG)': 128,
    # UEFA & European Tournaments
    'UEFA Champions League': 2, 'UEFA Europa League': 3, 'UEFA Conference League': 848, 
    'UEFA Super Cup': 531, 'UEFA Nations League': 5,
    # Major League Cups
    'FA Cup (ENG)': 45, 'EFL Cup (ENG)': 48, 'Copa del Rey (ESP)': 143, 
    'Coppa Italia (ITA)': 137, 'DFB Pokal (GER)': 81, 'Coupe de France (FRA)': 66, 
    'KNVB Beker (NED)': 89, 'Taça de Portugal (POR)': 96, 'Copa do Brasil (BRA)': 73,
}

# ==========================================
# 3. API FUNCTIONS
# ==========================================
def get_fixtures(date_str):
    url = f"{BASE_URL}/fixtures"
    params = {'date': date_str, 'timezone': 'UTC'}
    headers = {'x-apisports-key': API_KEY}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        return response.json().get('response', [])
    except Exception as e:
        st.error(f"Error fetching fixtures: {e}")
        return []

def get_odds(fixture_id):
    url = f"{BASE_URL}/odds"
    params = {'fixture': fixture_id}
    headers = {'x-apisports-key': API_KEY}
    try:
        time.sleep(1.2) # Respect API rate limits
        response = requests.get(url, headers=headers, params=params, timeout=15)
        data = response.json().get('response', [])
        return data[0] if data else None
    except:
        return None

def calculate_confidence(odds_data):
    if not odds_data: return None, None, None
    try:
        bookmakers = odds_data.get('bookmakers', [])
        if not bookmakers: return None, None, None
        
        bets = bookmakers[0].get('bets', [])
        match_1x2 = next((b for b in bets if b.get('name') == 'Match Winner'), None)
        if not match_1x2: return None, None, None
        
        values = match_1x2.get('values', [])
        odds_dict = {v['value']: float(v['odd']) for v in values}
        
        # Calculate true implied probability (removing bookmaker margin)
        total_inverse = sum(1/o for o in odds_dict.values())
        probs = {k: (1/v) / total_inverse for k, v in odds_dict.items()}
        
        best_outcome = max(probs, key=probs.get)
        confidence = probs[best_outcome]
        odds_val = odds_dict[best_outcome]
        
        return best_outcome, confidence, odds_val
    except:
        return None, None, None

# ==========================================
# 4. STREAMLIT UI & MAIN LOGIC
# ==========================================
today = datetime.now()
selected_date = st.sidebar.date_input("📅 Select Date", today)
date_str = selected_date.strftime('%Y-%m-%d')

if st.sidebar.button(" Generate Predictions", type="primary"):
    with st.spinner(f"Fetching fixtures for {date_str}..."):
        fixtures = get_fixtures(date_str)
        
        if not fixtures:
            st.warning(f"⚠️ No fixtures found for {date_str}. Try a different date.")
            st.stop()
        
        league_ids = set(LEAGUES.values())
        league_fixtures = [f for f in fixtures if f.get('league', {}).get('id') in league_ids]
        
        st.info(f" Found {len(league_fixtures)} fixtures in tracked leagues.")
        
        all_predictions = []
        
        # Progress bar
        progress_bar = st.progress(0)
        total_fixtures = len(league_fixtures)
        
        for i, fixture in enumerate(league_fixtures):
            try:
                fixture_id = fixture['fixture']['id']
                odds_data = get_odds(fixture_id)
                
                if not odds_data: 
                    progress_bar.progress((i + 1) / total_fixtures)
                    continue
                
                outcome, confidence, odds_val = calculate_confidence(odds_data)
                
                # Filter: Only keep games with > 70% confidence
                if outcome and confidence and confidence >= 0.70:
                    all_predictions.append({
                        'league': fixture.get('league', {}).get('name', ''),
                        'home_team': fixture['teams']['home']['name'],
                        'away_team': fixture['teams']['away']['name'],
                        'outcome': outcome,
                        'confidence': confidence,
                        'odds': odds_val,
                        'kickoff': fixture['fixture']['date'][11:16]
                    })
            except:
                pass
            
            progress_bar.progress((i + 1) / total_fixtures)
        
        st.success(f"✅ Found {len(all_predictions)} high-confidence predictions (>70%)!")
        
        if not all_predictions:
            st.info("No predictions met the 70% threshold today. Try lowering the threshold or checking a different date.")
            st.stop()
        
        # Sort by highest confidence
        all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        # ==========================================
        # 5. ORGANIZE INTO 4 FOLDERS OF 3 ODDS EACH
        # ==========================================
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
                    st.info(f"No {label} predictions found today.")

st.markdown("---")
st.markdown(f" Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")