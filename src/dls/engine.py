import math
from typing import Tuple

from dls.resource_table import ResourceTable


class DLSEngineError(ValueError):
    pass


class DLSEngine:
    def __init__(self, resource_table_path: str):
        self.resource_table = ResourceTable(resource_table_path)

    def compute_team1_resources_used(
        self, overs_faced: float, wickets_lost: int
    ) -> float:
        """
        Compute Team 1 resources used (%).

        If Team 1 bats full 50 overs, resources used = 100%.
        Otherwise, compute from remaining resources.
        """
        if overs_faced >= 50.0:
            return 100.0

        overs_remaining = 50.0 - overs_faced

        resource_remaining = self.resource_table.get_resource(
            overs_remaining, wickets_lost
        )

        return 100.0 - resource_remaining

    def compute_team2_resources_available(
        self, overs_remaining: float, wickets_lost: int
    ) -> float:
        """
        Compute Team 2 resources available (%).
        """
        return self.resource_table.get_resource(
            overs_remaining, wickets_lost
        )

    def compute_par_score(
        self,
        team1_score: int,
        team1_resources_used: float,
        team2_resources_available: float,
    ) -> float:
        """
        Compute par score (can be fractional).
        """
        if team1_resources_used <= 0:
            raise DLSEngineError("Team 1 resources used must be > 0")

        return team1_score * (
            team2_resources_available / team1_resources_used
        )

    def compute_revised_target(
        self,
        team1_score: int,
        team1_resources_used: float,
        team2_resources_available: float,
    ) -> int:
        """
        Compute revised target (integer).
        """
        par_score = self.compute_par_score(
            team1_score,
            team1_resources_used,
            team2_resources_available,
        )

        return math.floor(par_score) + 1

    def decide_match_outcome(
    self,
    match_status: str,
    team2_score: int,
    par_score: float,
    revised_target: int,
    ) -> dict:
        """
        Decide match outcome based on DLS rules.
        """
        if match_status == "abandoned":
            if team2_score > par_score:
                result = "Team 2 wins"
            elif team2_score < par_score:
                result = "Team 1 wins"
            else:
                result = "Match tied"

            return {
                "result": result,
                "par_score": round(par_score, 2),
                "team2_score": team2_score,
            }

        elif match_status == "resumed":
            runs_needed = max(0, revised_target - team2_score)

            return {
                "result": "Match resumed",
                "revised_target": revised_target,
                "team2_score": team2_score,
                "runs_needed": runs_needed,
            }

        else:
            raise DLSEngineError("Invalid match status")