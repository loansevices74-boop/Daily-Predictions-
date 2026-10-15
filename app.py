import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from src.api_client import FootballAPI
from src.prediction_model import PredictionModel
from config import API_KEY, BASE_URL, LEAGUES, CONFIDENCE_THRESHOLD

st.set_page_config(page_title="Football Predictor", layout="wide")

st.title(" Football Prediction System")
st.markdown("### Daily High-Confidence Picks (>70%)")

# Debug mode
debug = st.sidebar.checkbox("🔍 Debug Mode", value=False)

if not API_KEY:
    st.error(" API Key not configured! Add ODD_API_KEY to Streamlit Secrets.")
    st.stop()

# Initialize
api = FootballAPI(API_KEY, BASE_URL)
model = PredictionModel()

# Date selection - default to TODAY
today = datetime.now()
selected_date = st.sidebar.date_input("Select Date", today)
date_str = selected_date.strftime('%Y-%m-%d')

st.sidebar.markdown(f"**Selected Date:** {date_str}")
st.sidebar.markdown(f"**API Key:** {'✅ Set' if API_KEY else ' Missing'}")

if st.sidebar.button("🔄 Generate Predictions", type="primary"):
    with st.spinner(f"Fetching fixtures for {date_str}..."):
        all_predictions = []
        errors = []
        
        # Fetch fixtures for ALL leagues at once (more efficient)
        fixtures = api.get_daily_fixtures(date_str)
        
        if debug:
            st.write(f"📊 Total fixtures fetched: {len(fixtures)}")
        
        if not fixtures:
            st.warning(f"⚠️ No fixtures found for {date_str}. Try a different date.")
            st.stop()
        
        # Filter to our leagues
        league_ids = set(LEAGUES.values())
        league_fixtures = [f for f in fixtures if f.get('league', {}).get('id') in league_ids]
        
        if debug:
            st.write(f"🏆 League fixtures: {len(league_fixtures)}")
        
        # Process each fixture
        for fixture in league_fixtures:
            try:
                fixture_id = fixture['fixture']['id']
                league_name = fixture.get('league', {}).get('name', 'Unknown')
                
                if debug:
                    st.write(f"Processing: {fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}")
                
                odds_data = api.get_odds(fixture_id)
                
                if not odds_data:
                    if debug:
                        st.write(f"  ⚠️ No odds available")
                    continue
                
                prediction = model.predict_outcome(fixture, odds_data)
                
                if not prediction:
                    continue
                
                # Only keep predictions above threshold
                if prediction['confidence'] >= CONFIDENCE_THRESHOLD:
                    prediction['fixture_data'] = fixture
                    prediction['league'] = league_name
                    prediction['home_team'] = fixture['teams']['home']['name']
                    prediction['away_team'] = fixture['teams']['away']['name']
                    prediction['kickoff'] = fixture['fixture']['date'][11:16]
                    all_predictions.append(prediction)
                
            except Exception as e:
                errors.append(str(e))
                continue
        
        if debug and errors:
            st.error(f"Errors: {errors[:5]}")
        
        st.success(f"✅ Found {len(all_predictions)} high-confidence predictions!")
        
        if not all_predictions:
            st.info("💡 No predictions met the 70% threshold. Try lowering it or checking a different date.")
            
            # Show what we did find
            st.markdown("**Top predictions (below threshold):**")
            # Re-fetch to show top ones
            top_preds = []
            for fixture in league_fixtures[:20]:
                odds_data = api.get_odds(fixture['fixture']['id'])
                if odds_data:
                    pred = model.predict_outcome(fixture, odds_data)
                    if pred:
                        pred['home_team'] = fixture['teams']['home']['name']
                        pred['away_team'] = fixture['teams']['away']['name']
                        pred['league'] = fixture.get('league', {}).get('name', '')
                        pred['kickoff'] = fixture['fixture']['date'][11:16]
                        top_preds.append(pred)
            
            if top_preds:
                top_preds.sort(key=lambda x: x['confidence'], reverse=True)
                df_top = pd.DataFrame([{
                    'League': p['league'],
                    'Match': f"{p['home_team']} vs {p['away_team']}",
                    'Pick': p['outcome'],
                    'Confidence': f"{p['confidence']:.1%}",
                    'Odds': f"{p['odds']:.2f}",
                    'Time': p['kickoff']
                } for p in top_preds[:10]])
                st.dataframe(df_top, use_container_width=True)
            st.stop()
        
        # Organize into 4 folders
        folder1 = [p for p in all_predictions if p['outcome'] == 'Home' and 1.3 <= p['odds'] <= 2.2][:3]
        folder2 = [p for p in all_predictions if p['outcome'] == 'Draw' and 2.8 <= p['odds'] <= 4.5][:3]
        folder3 = [p for p in all_predictions if p['outcome'] == 'Away' and 1.5 <= p['odds'] <= 3.0][:3]
        folder4 = [p for p in all_predictions if p['odds'] >= 2.5][:3]
        
        # Fill empty folders with best remaining
        used = set()
        for folder in [folder1, folder2, folder3, folder4]:
            for p in folder:
                used.add(p['fixture_data']['fixture']['id'])
        
        remaining = [p for p in all_predictions if p['fixture_data']['fixture']['id'] not in used]
        remaining.sort(key=lambda x: x['confidence'], reverse=True)
        
        for folder in [folder1, folder2, folder3, folder4]:
            while len(folder) < 3 and remaining:
                folder.append(remaining.pop(0))
        
        # Display
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏠 Home Wins",
            "🤝 Draws", 
            "✈️ Away Wins",
            " High Value"
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