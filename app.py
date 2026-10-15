import streamlit as st
import pandas as pd
from datetime import datetime
from src.api_client import FootballAPI
from src.prediction_model import PredictionModel
from config import API_KEY, BASE_URL, LEAGUES, CONFIDENCE_THRESHOLD

st.set_page_config(page_title="Football Predictor", layout="wide")

st.title("🏆 Football Prediction System")
st.markdown("### Daily High-Confidence Picks (>70%)")

# Show API key status (masked)
if API_KEY:
    masked = API_KEY[:4] + "****" + API_KEY[-4:] if len(API_KEY) > 8 else "****"
    st.sidebar.success(f"✅ API Key: {masked}")
else:
    st.sidebar.error("❌ API Key missing")
    st.error("⚠️ API Key not configured! Add `ODD_API_KEY` to Streamlit Secrets.")
    st.stop()

api = FootballAPI(API_KEY, BASE_URL)
model = PredictionModel()

today = datetime.now()
selected_date = st.sidebar.date_input(" Select Date", today)
date_str = selected_date.strftime('%Y-%m-%d')

if st.sidebar.button("🔄 Generate Predictions", type="primary"):
    with st.spinner(f"Fetching fixtures for {date_str}..."):
        fixtures = api.get_daily_fixtures(date_str)
        
        if not fixtures:
            st.warning(f"⚠️ No fixtures found for {date_str}")
            st.stop()
        
        st.info(f"📊 Found {len(fixtures)} total fixtures today")
        
        league_ids = set(LEAGUES.values())
        league_fixtures = [f for f in fixtures if f.get('league', {}).get('id') in league_ids]
        
        st.info(f"🏆 {len(league_fixtures)} fixtures in tracked leagues")
        
        all_predictions = []
        
        for fixture in league_fixtures:
            try:
                fixture_id = fixture['fixture']['id']
                odds_data = api.get_odds(fixture_id)
                
                if not odds_data:
                    continue
                
                prediction = model.predict_outcome(fixture, odds_data)
                
                if not prediction:
                    continue
                
                if prediction['confidence'] >= CONFIDENCE_THRESHOLD:
                    prediction['league'] = fixture.get('league', {}).get('name', '')
                    prediction['home_team'] = fixture['teams']['home']['name']
                    prediction['away_team'] = fixture['teams']['away']['name']
                    prediction['kickoff'] = fixture['fixture']['date'][11:16]
                    prediction['fixture_id'] = fixture_id
                    all_predictions.append(prediction)
                    
            except Exception as e:
                continue
        
        st.success(f"✅ Found {len(all_predictions)} high-confidence predictions!")
        
        if not all_predictions:
            st.info("No predictions met the 70% threshold today.")
            st.stop()
        
        # Sort by confidence
        all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        # 4 folders of 3 odds each
        folder1 = [p for p in all_predictions if p['outcome'] == 'Home'][:3]
        folder2 = [p for p in all_predictions if p['outcome'] == 'Draw'][:3]
        folder3 = [p for p in all_predictions if p['outcome'] == 'Away'][:3]
        
        # Folder 4: highest odds
        folder4 = sorted(all_predictions, key=lambda x: x['odds'], reverse=True)[:3]
        
        tab1, tab2, tab3, tab4 = st.tabs([
            " Home Wins",
            "🤝 Draws",
            "✈️ Away Wins",
            "💎 High Value"
        ])
        
        for tab, folder, label in zip(
            [tab1, tab2, tab3, tab4],
            [folder1, folder2, folder3, folder4],
            ["Home Wins", "Draws", "Away Wins", "High Value"]
        ):
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