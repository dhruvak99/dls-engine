import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dls.pipeline import run_dls_pipeline
from dls.errors import InputValidationError


def print_demo_output(input_data, result):
    team1 = input_data["team1"]
    team2 = input_data["team2"]

    print("\n========== DLS DEMO ==========\n")

    print("Match Status:", input_data["match_status"])
    print("\nTeam 1:")
    print(f"  Score   : {team1['score']}")
    print(f"  Overs   : {team1['overs_faced']}")
    print(f"  Wickets : {team1['wickets_lost']}")

    print("\nTeam 2:")
    print(f"  Score   : {team2['runs_scored']}")
    print(f"  Overs   : {team2['overs_faced']}")
    print(f"  Wickets : {team2['wickets_lost']}")
    print(f"  Overs Remaining : {team2['scheduled_overs'] - team2['overs_faced']}")

    print("\nDLS Decision:")
    print(f"  Result         : {result['decision']['result']}")
    print(f"  Revised Target : {result['decision'].get('revised_target', 'N/A')}")
    print(f"  Runs Needed    : {result['decision'].get('runs_needed', 'N/A')}")

    print("\n==============================\n")


def main(input_path: str):
    input_file = Path(input_path)

    if not input_file.exists():
        print(f"❌ Input file not found: {input_path}")
        sys.exit(1)

    with open(input_file, "r") as f:
        input_data = json.load(f)

    try:
        RESOURCE_TABLE = "data/derived/resource_table_empirical_final.csv"
        result = run_dls_pipeline(input_data, RESOURCE_TABLE)
        print_demo_output(input_data, result)
    except InputValidationError as e:
        print("❌ Invalid input:", e)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/run_demo.py <input_json>")
        sys.exit(1)

    main(sys.argv[1])