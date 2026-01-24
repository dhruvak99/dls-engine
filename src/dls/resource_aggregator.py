from collections import defaultdict
from typing import Dict, List, Tuple

State = Dict[str, float]
Key = Tuple[float, int]


class ResourceAggregator:
    def __init__(self):
        # (overs_bucket, wickets_lost) -> list of runs_remaining
        self._data = defaultdict(list)

    def add_match_states(self, states: List[State]) -> None:
        for s in states:
            key = (s["overs_bucket"], s["wickets_lost"])
            self._data[key].append(s["runs_remaining"])

    def get_aggregates(self) -> Dict[Key, List[float]]:
        return self._data

    def compute_mean_runs(self) -> Dict[Key, float]:
        """
        Compute mean runs remaining for each (overs_bucket, wickets_lost).
        """
        mean_table = {}

        for key, values in self._data.items():
            if len(values) == 0:
                continue
            mean_table[key] = sum(values) / len(values)

        return mean_table

    def compute_resource_percentages(self) -> Dict[Key, float]:
        """
        Normalize mean runs remaining into resource percentages.
        """
        mean_table = self.compute_mean_runs()

        baseline_key = (50.0, 0)
        if baseline_key not in mean_table:
            raise ValueError(
                "Baseline (50.0 overs, 0 wickets) not found for normalization"
            )

        baseline = mean_table[baseline_key]

        resource_table = {}
        for key, mean_runs in mean_table.items():
            resource_table[key] = (mean_runs / baseline) * 100.0

        return resource_table