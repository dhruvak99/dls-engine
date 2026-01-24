import json
from pathlib import Path
from typing import List, Dict


class MatchParseError(ValueError):
    pass


TOTAL_OVERS = 50.0
BALLS_PER_OVER = 6


def bucket_overs_half(overs_remaining: float) -> float:
    """
    Bucket overs to nearest lower 0.5
    """
    return int(overs_remaining * 2) / 2


def parse_first_innings(json_path: str) -> List[Dict]:
    """
    Parse first-innings ball-by-ball data from a Cricsheet JSON file.

    Returns a list of state snapshots, one per delivery.
    """
    path = Path(json_path)

    if not path.exists():
        raise MatchParseError(f"File not found: {json_path}")

    with open(path, "r") as f:
        match = json.load(f)

    try:
        innings = match["innings"][0]  # first innings
        overs = innings["overs"]
    except (KeyError, IndexError) as e:
        raise MatchParseError("Invalid Cricsheet innings structure") from e

    # -------- First pass: compute final score --------
    final_score = 0
    for over in overs:
        for delivery in over["deliveries"]:
            final_score += delivery["runs"]["total"]

    # -------- Second pass: track state per ball --------
    states = []

    balls_bowled = 0
    runs_scored = 0
    wickets_lost = 0

    total_balls = int(TOTAL_OVERS * BALLS_PER_OVER)

    for over in overs:
        for delivery in over["deliveries"]:
            is_legal = True
            if "extras" in delivery:
                if "wides" in delivery["extras"] or "noballs" in delivery["extras"]:
                    is_legal = False

            if is_legal:
                balls_bowled += 1
            runs_scored += delivery["runs"]["total"]

            if "wickets" in delivery:
                wickets_lost += len(delivery["wickets"])

            balls_remaining = max(0,total_balls - balls_bowled)
            overs_remaining = balls_remaining / BALLS_PER_OVER
            overs_bucket = bucket_overs_half(overs_remaining)
            runs_remaining = final_score - runs_scored

            states.append(
                {
                    "overs_remaining": round(overs_remaining, 2),
                    "overs_bucket": overs_bucket,
                    "wickets_lost": wickets_lost,
                    "runs_remaining": runs_remaining,
                }
            )

    return states