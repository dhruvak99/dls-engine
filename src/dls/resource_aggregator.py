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