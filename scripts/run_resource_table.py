from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from dls.resource_table import ResourceTable, ResourceTableError


if __name__ == "__main__":
    rt = ResourceTable("data/resource_table.csv")

    try:
        value = rt.get_resource(20, 0)
        print("Resource(20 overs, 0 wickets):", value)
    except ResourceTableError as e:
        print("ERROR:", e)