"""Deterministic market-implied prediction model."""
from __future__ import annotations
from typing import Any

class PredictionModel:
    MARKET_NAME = "Match Winner"

    def calculate_implied_probability(self, odds_data: dict[str, Any] | None):
        if not odds_data:
            return None
        bookmakers = odds_data.get("bookmakers", [])
        if not bookmakers:
            return None
        market = next((b for b in bookmakers[0].get("bets", []) if b.get("name") == self.MARKET_NAME), None)
        if not market:
            return None
        odds: dict[str, float] = {}
        for value in market.get("values", []):
            try:
                odd = float(value["odd"])
                if odd > 1:
                    odds[str(value["value"])] = odd
            except (KeyError, TypeError, ValueError):
                continue
        if len(odds) < 2:
            return None
        inverse_total = sum(1 / odd for odd in odds.values())
        probabilities = {outcome: (1 / odd) / inverse_total for outcome, odd in odds.items()}
        return probabilities, odds

    def predict_outcome(self, fixture_data: dict[str, Any], odds_data: dict[str, Any] | None):
        result = self.calculate_implied_probability(odds_data)
        if not result:
            return None
        probabilities, odds = result
        outcome = max(probabilities, key=probabilities.get)
        return {"fixture_id": fixture_data.get("fixture", {}).get("id"), "outcome": outcome, "confidence": probabilities[outcome], "odds": odds[outcome], "all_probs": probabilities, "all_odds": odds}
