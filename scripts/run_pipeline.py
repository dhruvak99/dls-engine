from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dls.pipeline import run_dls_pipeline


if __name__ == "__main__":
    with open("examples/valid_input.json", "r") as f:
        input_data = json.load(f)

    output = run_dls_pipeline(
        input_data=input_data,
        resource_table_path="data/derived/resource_table_empirical.csv",
    )

    print("\nDLS PIPELINE OUTPUT:")
    for k, v in output.items():
        print(f"{k}: {v}")