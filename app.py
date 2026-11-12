import os
from datetime import date

import pandas as pd
import streamlit as st

from config import API_MIN_INTERVAL_SECONDS, API_KEY_ENV, BASE_URL, CONFIDENCE_THRESHOLD, REQUEST_TIMEOUT_SECONDS
from src.agent import explain_prediction
from src.api_client import FootballAPI, FootballAPIError
from src.confidence_filter import ConfidenceFilter
from src.pipeline import build_daily_predictions

st.set_page_config(page_title="Daily Football Predictions", page_icon="⚽", layout="wide")
st.title("⚽ Daily Football Predictions")
st.caption("Transparent market-implied estimates. Not guaranteed outcomes or financial advice.")


def secret(name: str) -> str:
    try:
        return str(st.secrets.get(name, ""))
    except Exception:
        return os.getenv(name, "")


api_key = secret(API_KEY_ENV)
if not api_key or api_key == "replace-me":
    st.error(f"Configure `{API_KEY_ENV}` in Streamlit secrets or the deployment environment.")
    st.stop()

selected_date = st.sidebar.date_input("Fixture date", value=date.today())
threshold = st.sidebar.slider("Minimum confidence", 0.34, 0.90, float(CONFIDENCE_THRESHOLD), 0.01)
refresh = st.sidebar.button("Refresh predictions", type="primary")

@st.cache_data(ttl=300, show_spinner=False)
def load_predictions(date_value: str, threshold_value: float):
    api = FootballAPI(api_key, BASE_URL, REQUEST_TIMEOUT_SECONDS, API_MIN_INTERVAL_SECONDS)
    predictions = build_daily_predictions(api, date.fromisoformat(date_value))
    return ConfidenceFilter(threshold_value).filter_high_confidence(predictions)

if refresh or "predictions" not in st.session_state:
    try:
        with st.spinner("Fetching fixtures and odds…"):
            st.session_state.predictions = load_predictions(selected_date.isoformat(), threshold)
        st.session_state.loaded_date = selected_date.isoformat()
    except (FootballAPIError, ValueError) as exc:
        st.error(f"Unable to load predictions: {exc}")
        st.stop()

predictions = st.session_state.predictions
st.metric("Qualified picks", len(predictions))
st.caption(f"Date: {st.session_state.get('loaded_date', selected_date.isoformat())} UTC")

if not predictions:
    st.info("No tracked fixtures currently meet the selected confidence threshold.")
else:
    rows = [{
        "League": p["league"],
        "Match": f"{p['home_team']} vs {p['away_team']}",
        "Pick": p["outcome"],
        "Confidence": f"{p['confidence']:.1%}",
        "Odds": f"{p['odds']:.2f}",
        "Kickoff UTC": p["kickoff"],
    } for p in predictions]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.subheader("AI-assisted explanations")
    for prediction in predictions[:10]:
        with st.expander(f"{prediction['home_team']} vs {prediction['away_team']} — {prediction['outcome']}"):
            st.write(explain_prediction(prediction))

st.divider()
st.caption("The core estimate is calculated from normalized bookmaker odds. AI explanations are optional and never replace the deterministic calculation.")
