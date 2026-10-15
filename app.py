import streamlit as st
import pandas as pd
from datetime import datetime
from src.api_client import FootballAPI
from src.prediction_model import PredictionModel
from src.confidence_filter import ConfidenceFilter
from config import LEAGUES

st.set_page_config(page_title="Football Predictor", layout="wide")

st.title("🏆 Football Prediction System")
st.markdown("### Daily High-Confidence Picks (>70%)")

# Initialize
api = FootballAPI()
model = PredictionModel()
filter_engine = ConfidenceFilter()

# Sidebar
st.sidebar.header("Settings")
selected_date = st.sidebar.date_input("Select Date", datetime.now())
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)

if st.sidebar.button("Generate Predictions"):
    with st.spinner("Fetching fixtures and analyzing..."):
        # Get all fixtures
        all_predictions = []
        
        for league_name, league_id in LEAGUES.items():
            fixtures = api.get_league_fixtures(league_id, selected_date.strftime('%Y-%m-%d'))
            
            for fixture in fixtures:
                odds_data = api.get_odds(fixture['fixture']['id'])
                prediction = model.predict_outcome(fixture, odds_data)
                
                prediction['fixture'] = fixture
                prediction['league'] = league_name
                
                if odds_data:
                    try:
                        bookmaker = odds_data[0]['bookmakers'][0]
                        bets = bookmaker['bets'][0]
                        for outcome in bets['values']:
                            if outcome['value'] == prediction['outcome']:
                                prediction['odds'] = float(outcome['odd'])
                                break
                    except:
                        prediction['odds'] = 0
                
                all_predictions.append(prediction)
        
        # Filter high confidence
        high_conf = filter_engine.filter_high_confidence(all_predictions)
        
        # Organize into folders
        folders = filter_engine.organize_by_odds(high_conf)
        
        # Display results
        st.success(f"Found {len(high_conf)} high-confidence predictions!")
        
        # Create tabs for each folder
        tab1, tab2, tab3, tab4 = st.tabs([
            "🏠 Home Wins (1.5-2.0)",
            "🤝 Draws (3.0-4.0)",
            "✈️ Away Wins (2.0-3.0)",
            "💎 High Value (>3.0)"
        ])
        
        for tab, folder_key in zip([tab1, tab2, tab3, tab4], folders.keys()):
            with tab:
                predictions = folders[folder_key]
                if predictions:
                    df = pd.DataFrame([{
                        'League': p['league'],
                        'Home': p['fixture']['teams']['home']['name'],
                        'Away': p['fixture']['teams']['away']['name'],
                        'Prediction': p['outcome'],
                        'Confidence': f"{p['confidence']:.1%}",
                        'Odds': f"{p['odds']:.2f}",
                        'Time': p['fixture']['fixture']['date'][11:16]
                    } for p in predictions])
                    
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No predictions in this category")

# Footer
st.markdown("---")
st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")