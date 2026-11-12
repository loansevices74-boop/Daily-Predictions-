"""Optional AI explanation layer."""
from __future__ import annotations
import os
import requests

def explain_prediction(prediction: dict) -> str:
    endpoint = os.getenv("AI_AGENT_ENDPOINT")
    model = os.getenv("AI_AGENT_MODEL", "local-model")
    if not endpoint:
        return "Market-implied estimate based on available odds; no LLM explanation configured."
    prompt = "Explain this football prediction in one cautious sentence. Do not claim certainty or recommend gambling. Use only these facts:\n" + str(prediction)
    try:
        response = requests.post(endpoint, json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.2}, timeout=15)
        response.raise_for_status()
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No explanation available.")
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        return "AI explanation unavailable; the displayed estimate is calculated from bookmaker odds."
