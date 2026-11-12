"""Small, testable API-Football client."""
from __future__ import annotations
import time
from datetime import date
from typing import Any
import requests

class FootballAPIError(RuntimeError):
    pass

class FootballAPI:
    def __init__(self, api_key: str, base_url: str, timeout: int = 20, min_interval: float = 0.25):
        if not api_key:
            raise ValueError("FOOTBALL_API_KEY is required")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.min_interval = min_interval
        self.session = requests.Session()
        self.session.headers.update({"x-apisports-key": api_key})
        self._last_request = 0.0

    def _get(self, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        try:
            response = self.session.get(f"{self.base_url}/{path.lstrip('/')}", params=params, timeout=self.timeout)
            self._last_request = time.monotonic()
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as exc:
            raise FootballAPIError(f"Football API request failed: {exc}") from exc
        if payload.get("errors"):
            raise FootballAPIError(str(payload["errors"]))
        return payload.get("response", [])

    def get_daily_fixtures(self, fixture_date: date | str) -> list[dict[str, Any]]:
        value = fixture_date.isoformat() if isinstance(fixture_date, date) else fixture_date
        return self._get("fixtures", {"date": value, "timezone": "UTC"})

    def get_odds(self, fixture_id: int) -> dict[str, Any] | None:
        results = self._get("odds", {"fixture": fixture_id})
        return results[0] if results else None
