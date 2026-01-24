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

    mean_table = agg.compute_mean_runs()

    print("\nSample mean values:")
    for k in list(mean_table.keys())[:5]:
        print(k, "->", round(mean_table[k], 2))

    resource_table = agg.compute_resource_percentages()

    print("\nSample resource percentages:")
    for k in list(resource_table.keys())[:10]:
        print(k, "->", round(resource_table[k], 2))

    output_csv = "data/derived/resource_table_empirical.csv"
    agg.export_resource_table_csv(output_csv)

    print(f"\nResource table exported to: {output_csv}")