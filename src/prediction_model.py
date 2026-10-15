import numpy as np

class PredictionModel:
    def __init__(self):
        pass
    
    def calculate_implied_probability(self, odds_data):
        """Convert bookmaker odds to true implied probability"""
        if not odds_data:
            return None
        
        try:
            bookmakers = odds_data.get('bookmakers', [])
            if not bookmakers:
                return None
            
            # Use first bookmaker's 1X2 market
            bets = bookmakers[0].get('bets', [])
            match_1x2 = None
            for bet in bets:
                if bet.get('name') == 'Match Winner':
                    match_1x2 = bet
                    break
            
            if not match_1x2:
                return None
            
            values = match_1x2.get('values', [])
            odds_dict = {}
            for v in values:
                odds_dict[v['value']] = float(v['odd'])
            
            if len(odds_dict) < 3:
                return None
            
            # Remove bookmaker margin to get true probability
            total_inverse = sum(1/o for o in odds_dict.values())
            probs = {k: (1/v) / total_inverse for k, v in odds_dict.items()}
            
            return probs, odds_dict
        except Exception as e:
            print(f"Error calculating probability: {e}")
            return None
    
    def predict_outcome(self, fixture_data, odds_data):
        """Predict outcome using odds-implied probability"""
        result = self.calculate_implied_probability(odds_data)
        if not result:
            return None
        
        probs, odds_dict = result
        best_outcome = max(probs, key=probs.get)
        confidence = probs[best_outcome]
        odds = odds_dict.get(best_outcome, 0)
        
        return {
            'outcome': best_outcome,
            'probability': confidence,
            'confidence': confidence,  # Use implied prob as confidence
            'odds': odds,
            'all_probs': probs,
            'all_odds': odds_dict
        }