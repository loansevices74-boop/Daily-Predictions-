"""Daily prediction orchestration used by Streamlit and GitHub Actions."""
from __future__ import annotations
from datetime import date
from typing import Any
from config import TRACKED_LEAGUE_IDS
from src.api_client import FootballAPI
from src.prediction_model import PredictionModel

def build_daily_predictions(api: FootballAPI, selected_date: date, model: PredictionModel | None = None) -> list[dict[str, Any]]:
    model = model or PredictionModel()
    predictions = []
    for fixture in api.get_daily_fixtures(selected_date):
        if fixture.get("league", {}).get("id") not in TRACKED_LEAGUE_IDS:
            continue
        fixture_id = fixture.get("fixture", {}).get("id")
        if not fixture_id:
            continue
        prediction = model.predict_outcome(fixture, api.get_odds(fixture_id))
        if not prediction:
            continue
        prediction.update({"date": selected_date.isoformat(), "league": fixture.get("league", {}).get("name", "Unknown"), "home_team": fixture.get("teams", {}).get("home", {}).get("name", "Unknown"), "away_team": fixture.get("teams", {}).get("away", {}).get("name", "Unknown"), "kickoff": fixture.get("fixture", {}).get("date", "")[11:16]})
        predictions.append(prediction)
    return sorted(predictions, key=lambda item: item["confidence"], reverse=True)
