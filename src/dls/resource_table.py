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
        """
        Return resource percentage for given (overs_remaining, wickets_lost).
        Falls back gracefully if exact state is missing.
        """

        # Clamp inputs
        overs_remaining = max(0.0, overs_remaining)
        wickets_lost = min(10, max(0, wickets_lost))

        # --- Exact lookup ---
        key = (overs_remaining, wickets_lost)
        if key in self._table:
            return self._table[key]

        # --- Fallback 1: same overs, more wickets lost ---
        for w in range(wickets_lost + 1, 11):
            key = (overs_remaining, w)
            if key in self._table:
                return self._table[key]

        # --- Fallback 2: reduce overs in 0.5 steps ---
        o = overs_remaining
        while o >= 0:
            key = (o, wickets_lost)
            if key in self._table:
                return self._table[key]
            o = round(o - 0.5, 1)

        # --- Final fallback: no resources left ---
        return 0.0