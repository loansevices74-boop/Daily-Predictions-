from config import CONFIDENCE_THRESHOLD

class ConfidenceFilter:
    def __init__(self, threshold=CONFIDENCE_THRESHOLD):
        self.threshold = threshold
    
    def filter_high_confidence(self, predictions):
        """Filter predictions above confidence threshold"""
        return [p for p in predictions if p['confidence'] >= self.threshold]
    
    def organize_by_odds(self, predictions):
        """
        Organize into 4 folders of 3 odds each
        Folder 1: Home wins (odds 1.5-2.0)
        Folder 2: Draws (odds 3.0-4.0)
        Folder 3: Away wins (odds 2.0-3.0)
        Folder 4: High value (odds > 3.0)
        """
        folders = {
            'folder_1_home_wins': [],
            'folder_2_draws': [],
            'folder_3_away_wins': [],
            'folder_4_high_value': []
        }
        
        for pred in predictions:
            odds = pred.get('odds', 2.0)
            outcome = pred['outcome']
            
            if outcome == 'Home' and 1.5 <= odds <= 2.0:
                folders['folder_1_home_wins'].append(pred)
            elif outcome == 'Draw' and 3.0 <= odds <= 4.0:
                folders['folder_2_draws'].append(pred)
            elif outcome == 'Away' and 2.0 <= odds <= 3.0:
                folders['folder_3_away_wins'].append(pred)
            elif odds > 3.0:
                folders['folder_4_high_value'].append(pred)
        
        # Limit to 3 per folder
        for key in folders:
            folders[key] = folders[key][:3]
        
        return folders