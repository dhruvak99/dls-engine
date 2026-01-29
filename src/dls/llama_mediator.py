import requests
import json
import os


OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:30068"
)

MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.1:8b")


class LLaMAMediatorError(Exception):
    pass


def extract_dls_input(user_text: str) -> dict:
    """
    Uses LLaMA (via Ollama) to convert natural language cricket input
    into structured DLS JSON.
    """

    prompt = f"""
You are a cricket rules assistant.

Extract Duckworth-Lewis match parameters from the input below.

STRICT RULES:
- Return ONLY valid JSON
- Do NOT explain anything
- Do NOT guess missing values
- If information is missing, ask a clarification question instead
ASSUMPTIONS YOU ARE ALLOWED TO MAKE:
- The interruption is weather-related (rain) unless stated otherwise.
- Team 1 is the team that batted first.
- Team 2 is the team batting at the time of interruption.
- The match is resumed if overs are reduced and play continues.
- Overs reductions apply only to Team 2 (the team batting at interruption).
- Team 1’s innings is always treated as completed under original conditions.
FINAL INSTRUCTION:
If all values required by the DLS engine can be reasonably inferred using standard ODI and DLS rules,
DO NOT ask further clarification questions.
Only ask for clarification if a numeric value (score, overs, wickets) is missing or contradictory.

You MUST NOT ask questions about:
- Whether Team 1 completed its innings (assume yes)
- Whether overs reduction affects Team 1 (assume no)
- Whether wickets fell during interruption (assume no change)
- The reason for interruption (assume weather)
Required JSON schema:
{{
  "match_status": "resumed" or "abandoned",
  "team1": {{
    "score": int,
    "overs_faced": float,
    "wickets_lost": int
  }},
  "team2": {{
    "runs_scored": int,
    "overs_faced": float,
    "wickets_lost": int,
    "scheduled_overs": float
  }}
}}

Input:
\"\"\"{user_text}\"\"\"
"""

    try:
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=30
    )
    except requests.exceptions.RequestException as e:
        raise LLaMAMediatorError(
            f"LLaMA service unreachable at {OLLAMA_BASE_URL}. "
            "Check OLLAMA_URL configuration."
        ) from e

    if response.status_code != 200:
        raise LLaMAMediatorError(
            f"Ollama error: {response.status_code}"
        )

    raw_output = response.json().get("response", "").strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        # LLaMA is asking for clarification
        raise LLaMAMediatorError(raw_output)