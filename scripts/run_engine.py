from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dls.engine import DLSEngine


if __name__ == "__main__":
    engine = DLSEngine("data/derived/resource_table_empirical.csv")

    # Example scenario
    team1_score = 300
    team1_overs = 50.0
    team1_wickets = 7

    team2_overs_faced = 27.5
    team2_wickets_lost = 3
    total_overs = 40.0

    team2_overs_remaining = total_overs - team2_overs_faced

    r1_used = engine.compute_team1_resources_used(
        team1_overs, team1_wickets
    )
    r2_available = engine.compute_team2_resources_available(
        team2_overs_remaining, team2_wickets_lost
    )

    par = engine.compute_par_score(
        team1_score, r1_used, r2_available
    )
    target = engine.compute_revised_target(
        team1_score, r1_used, r2_available
    )

    print("Team 1 resources used (%):", round(r1_used, 2))
    print("Team 2 resources available (%):", round(r2_available, 2))
    print("Par score:", round(par, 2))
    print("Revised target:", target)

    outcome = engine.decide_match_outcome(
    match_status="resumed",
    team2_score=90,
    par_score=par,
    revised_target=target,
    )

    print("\nDecision:")
    for k, v in outcome.items():
        print(f"{k}: {v}")