# Daily Predictions

Streamlit dashboard for transparent daily football estimates using API-Football fixtures and odds.

## Features

- Current-date fixture selection; no stale hardcoded date.
- Normalized bookmaker-implied probabilities for Home, Draw, and Away.
- Confidence threshold and cached refresh controls in Streamlit.
- Optional OpenAI-compatible local agent endpoint for cautious explanations.
- Scheduled GitHub Actions job for daily JSON snapshots.
- Unit tests for probability and filtering logic.

## Configure locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FOOTBALL_API_KEY="your-new-api-key"
streamlit run app.py
```

For Streamlit Cloud, add `FOOTBALL_API_KEY` under App settings -> Secrets. Never commit API keys. The previously exposed key must be revoked and replaced.

Optional local agent settings:

```bash
export AI_AGENT_ENDPOINT="http://localhost:11434/v1/chat/completions"
export AI_AGENT_MODEL="llama3.2"
```

## GitHub Actions

Add a repository secret named `FOOTBALL_API_KEY`. The scheduled workflow runs at 08:00 UTC and can also be started manually. It runs tests, fetches current predictions, and commits the daily JSON snapshot.

## Limitations

The core estimate is derived from available bookmaker odds; it is not a calibrated guarantee, and missing odds produce no pick. AI explanations do not alter the deterministic estimate. Use responsibly and comply with local laws.
