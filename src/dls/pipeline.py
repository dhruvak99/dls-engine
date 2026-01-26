from dls.validator import validate_input
from dls.engine import DLSEngine
from dls.errors import InputValidationError
from dls.engine import DLSEngineError


class DLSPipelineError(ValueError):
    pass


def run_dls_pipeline(
    input_data: dict,
    resource_table_path: str,
) -> dict:
    """
    Full DLS pipeline:
    input -> validation -> engine -> decision
    """

    # ---------- Validation ----------
    try:
        validate_input(input_data)
    except InputValidationError as e:
        raise DLSPipelineError(f"Invalid input: {e}")

    # ---------- Extract fields ----------
    match_status = input_data["match_status"]

    team1 = input_data["team1"]
    team2 = input_data["team2"]

    team1_score = team1["score"]
    team1_overs = team1["overs_faced"]
    team1_wickets = team1["wickets_lost"]

    team2_score = team2["runs_scored"]
    team2_overs_faced = team2["overs_faced"]
    team2_wickets_lost = team2["wickets_lost"]
    total_overs = team2["scheduled_overs"]

    team2_overs_remaining = total_overs - team2_overs_faced

        # ---------- No DLS adjustment case ----------
    ORIGINAL_OVERS = 50.0

    if (
        match_status == "resumed"
        and abs(total_overs - ORIGINAL_OVERS) < 1e-6
    ):
        revised_target = team1_score + 1
        runs_needed = max(0, revised_target - team2_score)

        return {
            "team1_resources_used_pct": 100.0,
            "team2_resources_available_pct": 100.0,
            "expected_runs_remaining": round(
                max(0, revised_target - team2_score), 2
            ),
            "par_score": team1_score,
            "revised_target": revised_target,
            "decision": {
                "result": "Match resumed (no DLS adjustment)",
                "revised_target": revised_target,
                "team2_score": team2_score,
                "runs_needed": runs_needed,
            },
        }

    
    # ---------- Engine ----------
    engine = DLSEngine(resource_table_path)

    try:
        r1_used = engine.compute_team1_resources_used(
            team1_overs, team1_wickets
        )
        r2_available = engine.compute_team2_resources_available(
            team2_overs_remaining, team2_wickets_lost
        )

        # r2_available now represents expected runs remaining
        expected_runs_remaining = r2_available
        #below line scales the data over 50 overs, before used to get par score more than team 1 score
        expected_runs_remaining = r2_available * (total_overs / 50.0)
        expected_runs_remaining = max(0.0, expected_runs_remaining)

        #temp debug code starts
        # print("DEBUG total_overs:", total_overs)
        # print("DEBUG r2_available (raw):", r2_available)
        # print("DEBUG scale factor:", total_overs / 50.0)
        # print("DEBUG expected_runs_remaining (scaled):", expected_runs_remaining)
        #temp debug code ends
        par_score = team2_score + expected_runs_remaining
        revised_target = int(par_score) + 1

        decision = engine.decide_match_outcome(
            match_status=match_status,
            team2_score=team2_score,
            par_score=par_score,
            revised_target=revised_target,
        )

    except DLSEngineError as e:
        raise DLSPipelineError(f"Engine error: {e}")

    # ---------- Final output ----------
    return {
        "team1_resources_used_pct": round(r1_used, 2),
        "team2_resources_available_pct": round(r2_available, 2),
        "expected_runs_remaining": round(expected_runs_remaining,2),
        "par_score": round(par_score, 2),
        "revised_target": revised_target,
        "decision": decision,
    }