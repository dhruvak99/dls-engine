import math
from typing import Tuple

from dls.resource_table import ResourceTable


class DLSEngineError(ValueError):
    pass

def bucket_overs(overs: float) -> float:
    """
    Round DOWN to nearest 0.5 over.
    """
    return int(overs * 2) / 2

class DLSEngine:
    def __init__(self, resource_table_path: str):
        self.resource_table = ResourceTable(resource_table_path)

    def compute_team1_resources_used(
        self, overs_faced: float, wickets_lost: int
    ) -> float:
        """
        Compute Team 1 resources used (%).

        If Team 1 bats full 50 overs or is all out, resources used = 100%.
        Otherwise, compute from remaining resources.
        """

        # If Team 1 completed the innings, full resources used
        if overs_faced >= 50.0 or wickets_lost >= 10:
            return 100.0

        # Compute overs remaining
        overs_remaining = 50.0 - overs_faced

        # Bucket overs to match resource table resolution
        overs_bucketed = bucket_overs(overs_remaining)

        if overs_bucketed < 0:
            overs_bucketed = 0.0

        resource_remaining = self.resource_table.get_resource(
            overs_bucketed, wickets_lost
        )

        # 🔒 Clamp remaining resources to [0, 100]
        resource_remaining = max(0.0, min(resource_remaining, 100.0))

        return 100.0 - resource_remaining

    def compute_team2_resources_available(
        self, overs_remaining: float, wickets_lost: int
    ) -> float:
        # Bucket overs to match resource table resolution
        overs_bucketed = bucket_overs(overs_remaining)

        if overs_bucketed < 0:
            overs_bucketed = 0.0

        resource = self.resource_table.get_resource(
            overs_bucketed, wickets_lost
        )

        # 🔒 Clamp to valid range
        resource = max(0.0, min(resource, 100.0))

        return resource

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
    def compute_expected_score_at_overs(
        self,
        team2_score: int,
        par_score: float,
        overs_remaining_now: float,
        overs_remaining_future: float,
        wickets_lost: int,
    ) -> float:
        """
        Expected Team 2 score at a future overs_remaining point,
        anchored to the DLS par score.
        """

        now_bucket = bucket_overs(overs_remaining_now)
        future_bucket = bucket_overs(overs_remaining_future)

        if now_bucket <= 0:
            return team2_score

        res_now = self.resource_table.get_resource(now_bucket, wickets_lost)
        res_future = self.resource_table.get_resource(future_bucket, wickets_lost)

        # Clamp defensively
        res_now = max(0.0, min(res_now, 100.0))
        res_future = max(0.0, min(res_future, 100.0))

        # Fraction of remaining resources used
        # If no remaining resources now, score cannot increase
        # If no remaining resources now, score cannot increase
        if res_now <= 0:
            return team2_score

        fraction_completed = (res_now - res_future) / res_now
        expected_score = team2_score + fraction_completed * (par_score - team2_score)

        return expected_score