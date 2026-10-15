import numpy as np
from datetime import datetime

class PredictionModel:
    def __init__(self):
        self.model_type = "statistical"
    
    def calculate_confidence(self, fixture_data, odds_data):
        """
        Calculate confidence score based on:
        - Team form (last 5 matches)
        - Head-to-head record
        - Home/away performance
        - Odds consistency
        """
        confidence = 0.0
        
        # Extract key metrics
        home_form = self._get_team_form(fixture_data, 'home')
        away_form = self._get_team_form(fixture_data, 'away')
        h2h = self._get_h2h_record(fixture_data)
        odds_implied_prob = self._calculate_implied_probability(odds_data)
        
        # Form analysis (30% weight)
        form_diff = home_form - away_form
        confidence += abs(form_diff) * 0.3
        
        # H2H dominance (25% weight)
        if h2h['home_wins'] > h2h['away_wins'] * 1.5:
            confidence += 0.25
        elif h2h['away_wins'] > h2h['home_wins'] * 1.5:
            confidence += 0.25
        
        # Odds consistency (25% weight)
        max_prob = max(odds_implied_prob.values())
        if max_prob > 0.6:
            confidence += 0.25
        
        # Home advantage (20% weight)
        if fixture_data['fixture']['venue']['name']:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _get_team_form(self, fixture_data, team_type):
        """Calculate team form score (0-1)"""
        # This would use actual API data
        # Simplified version
        return np.random.uniform(0.4, 0.9)
    
    def _get_h2h_record(self, fixture_data):
        """Get head-to-head record"""
        # This would use actual API data
        return {
            'home_wins': np.random.randint(0, 5),
            'away_wins': np.random.randint(0, 5),
            'draws': np.random.randint(0, 3)
        }
    
    def _calculate_implied_probability(self, odds_data):
        """Convert odds to implied probability"""
        if not odds_data:
            return {'home': 0.33, 'draw': 0.33, 'away': 0.33}
        
        try:
            bookmaker = odds_data[0]['bookmakers'][0]
            bets = bookmaker['bets'][0]
            
            odds = {}
            for outcome in bets['values']:
                odds[outcome['value']] = float(outcome['odd'])
            
            # Convert to probability
            total = sum(1/o for o in odds.values())
            probs = {k: (1/v)/total for k, v in odds.items()}
            
            return probs
        except:
            return {'home': 0.33, 'draw': 0.33, 'away': 0.33}
    
    def predict_outcome(self, fixture_data, odds_data):
        """Predict most likely outcome"""
        probs = self._calculate_implied_probability(odds_data)
        max_outcome = max(probs, key=probs.get)
        
        return {
            'outcome': max_outcome,
            'probability': probs[max_outcome],
            'confidence': self.calculate_confidence(fixture_data, odds_data)
        }