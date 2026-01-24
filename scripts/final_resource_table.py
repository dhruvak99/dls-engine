from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dls.resource_aggregator import ResourceAggregator


# -------- Paths --------
BATCH_PATH = Path("data/derived/batches/batch_309.pkl")  # adjust if needed
OUTPUT_CSV = Path("data/derived/resource_table_empirical_final.csv")


def main():
    print(f"Loading full batch: {BATCH_PATH}")

    agg = ResourceAggregator.load(BATCH_PATH)

    print("Computing resource percentages...")
    resource_table = agg.compute_resource_percentages()

    print("Exporting final resource table...")
    agg.export_resource_table_csv(OUTPUT_CSV)

    print(f"✅ Final resource table written to {OUTPUT_CSV}")
    print(f"Total (overs, wickets) states: {len(resource_table)}")


if __name__ == "__main__":
    main()