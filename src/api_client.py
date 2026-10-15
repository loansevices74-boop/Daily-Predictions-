import requests
from config import API_KEY, BASE_URL, LEAGUES
from datetime import datetime, timedelta

class FootballAPI:
    def __init__(self):
        self.headers = {
            'x-apisports-key': API_KEY
        }
    
    def get_daily_fixtures(self, date=None):
        """Get all fixtures for today"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        url = f"{BASE_URL}/fixtures"
        params = {
            'date': date,
            'timezone': 'UTC'
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()['response']
    
    def get_odds(self, fixture_id):
        """Get odds for specific fixture"""
        url = f"{BASE_URL}/odds"
        params = {
            'fixture': fixture_id,
            'bookmaker': 8  # Pinnacle
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()['response']
    
    def get_league_fixtures(self, league_id, date=None):
        """Get fixtures for specific league"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        url = f"{BASE_URL}/fixtures"
        params = {
            'league': league_id,
            'season': 2026,
            'date': date
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()['response']