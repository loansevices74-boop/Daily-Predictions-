import requests
import time
from datetime import datetime

class FootballAPI:
    def __init__(self, api_key, base_url):
        self.headers = {'x-apisports-key': api_key}
        self.base_url = base_url
        self.last_request = 0
    
    def _rate_limit(self):
        """API allows 10 requests/minute - be safe"""
        elapsed = time.time() - self.last_request
        if elapsed < 7:
            time.sleep(7 - elapsed)
        self.last_request = time.time()
    
    def get_daily_fixtures(self, date=None):
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        self._rate_limit()
        try:
            url = f"{self.base_url}/fixtures"
            params = {'date': date, 'timezone': 'UTC'}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            data = response.json()
            
            if response.status_code != 200:
                print(f"API Error: {data}")
                return []
            
            return data.get('response', [])
        except Exception as e:
            print(f"Error fetching fixtures: {e}")
            return []
    
    def get_odds(self, fixture_id):
        self._rate_limit()
        try:
            url = f"{self.base_url}/odds"
            params = {'fixture': fixture_id}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            data = response.json()
            
            if response.status_code != 200:
                return None
            
            results = data.get('response', [])
            return results[0] if results else None
        except Exception as e:
            print(f"Error fetching odds for {fixture_id}: {e}")
            return None