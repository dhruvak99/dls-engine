import csv
from pathlib import Path


class ResourceTableError(ValueError):
    """Raised when resource table lookup fails."""
    pass


class ResourceTable:
    def __init__(self, csv_path: str):
        self._table = {}
        self._load(csv_path)

    def _load(self, csv_path: str) -> None:
        path = Path(csv_path)

        if not path.exists():
            raise ResourceTableError(f"Resource table not found: {csv_path}")

        with open(path, "r", newline="") as f:
            reader = csv.DictReader(f)

            required_cols = {"overs_remaining", "wickets_lost", "resource_pct"}
            if not required_cols.issubset(reader.fieldnames):
                raise ResourceTableError(
                    f"CSV must contain columns: {required_cols}"
                )

            for row in reader:
                overs = float(row["overs_remaining"])
                wickets = int(row["wickets_lost"])
                resource = float(row["resource_pct"])

                key = (overs, wickets)
                self._table[key] = resource

    def get_resource(self, overs_remaining: float, wickets_lost: int) -> float:
        key = (overs_remaining, wickets_lost)

        if key not in self._table:
            raise ResourceTableError(
                f"No resource entry for overs={overs_remaining}, wickets={wickets_lost}"
            )

        return self._table[key]