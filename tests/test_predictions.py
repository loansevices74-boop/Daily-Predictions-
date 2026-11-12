from src.confidence_filter import ConfidenceFilter
from src.prediction_model import PredictionModel

def test_probability_normalizes_market_margin():
    odds = {"bookmakers": [{"bets": [{"name": "Match Winner", "values": [{"value": "Home", "odd": "2.0"}, {"value": "Draw", "odd": "3.5"}, {"value": "Away", "odd": "4.0"}]}]}]}
    result = PredictionModel().calculate_implied_probability(odds)
    assert result is not None
    probabilities, prices = result
    assert abs(sum(probabilities.values()) - 1) < 1e-9
    assert prices["Home"] == 2.0

def test_invalid_odds_are_ignored():
    odds = {"bookmakers": [{"bets": [{"name": "Match Winner", "values": [{"value": "Home", "odd": "bad"}]}]}]}
    assert PredictionModel().calculate_implied_probability(odds) is None

def test_filter_sorts_and_applies_threshold():
    predictions = [{"outcome": "Home", "confidence": 0.6}, {"outcome": "Away", "confidence": 0.8}, {"outcome": "Draw", "confidence": 0.4}]
    assert [p["confidence"] for p in ConfidenceFilter(0.55).filter_high_confidence(predictions)] == [0.8, 0.6]
