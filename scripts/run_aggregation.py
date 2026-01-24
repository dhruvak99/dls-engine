from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dls.match_parser import parse_first_innings
from dls.resource_aggregator import ResourceAggregator


if __name__ == "__main__":
    agg = ResourceAggregator()

    # TEMP: test on a few matches only
    match_files = [
        "data/match1.json",
        "data/match2.json",
    ]

    for mf in match_files:
        states = parse_first_innings(mf)
        agg.add_match_states(states)

    data = agg.get_aggregates()

    print("Total (overs_bucket, wickets) states:", len(data))

    # Print a few example keys
    for k in list(data.keys())[:5]:
        print(k, "->", len(data[k]), "samples")