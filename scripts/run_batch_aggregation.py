from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dls.match_parser import parse_first_innings
from dls.resource_aggregator import ResourceAggregator


# ---------- Configuration ----------
RAW_DIR = Path("data/raw/cricsheet_json")
BATCH_DIR = Path("data/derived/batches")
BATCH_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 10   # 👈 THIS is where batch size lives


def main():
    files = sorted(RAW_DIR.glob("*.json"))

    batch_num = 1
    agg = ResourceAggregator()

    for i, file_path in enumerate(files, start=1):
        try:
            states = parse_first_innings(file_path)
            agg.add_match_states(states)
        except Exception as e:
            print(f"Skipping {file_path.name}: {e}")
            continue

        # ---------- Save checkpoint ----------
        if i % BATCH_SIZE == 0:
            batch_path = BATCH_DIR / f"batch_{batch_num:03d}.pkl"
            agg.save(batch_path)
            print(f"Saved {batch_path}")

            batch_num += 1

    # ---------- Save final partial batch ----------
    batch_path = BATCH_DIR / f"batch_{batch_num:03d}.pkl"
    agg.save(batch_path)
    print(f"Saved {batch_path} (final)")


if __name__ == "__main__":
    main()