from dls.errors import InputValidationError
def validate_input(data: dict) -> None:
    """
    Validates structured input for the DLS engine.
    Raises InputValidationError if input is invalid.
    Returns None if input is valid.
    """

    # ---------- Top-level ----------
    if not isinstance(data, dict):
        raise InputValidationError("Input must be a dictionary")

    # ---------- Match status ----------
    match_status = data.get("match_status")
    if match_status not in {"resumed", "abandoned"}:
        raise InputValidationError(
            "match_status must be either 'resumed' or 'abandoned'"
        )

    # ---------- Team 1 ----------
    team1 = data.get("team1")
    if not isinstance(team1, dict):
        raise InputValidationError("team1 must be provided as an object")

    _validate_team1(team1)

    # ---------- Team 2 ----------
    team2 = data.get("team2")
    if not isinstance(team2, dict):
        raise InputValidationError("team2 must be provided as an object")

    _validate_team2(team2, match_status)


def _validate_team1(team1: dict) -> None:
    score = team1.get("score")
    overs_faced = team1.get("overs_faced")
    wickets_lost = team1.get("wickets_lost")

    if score is None or score < 0:
        raise InputValidationError("team1.score must be >= 0")

    if overs_faced is None or overs_faced <= 0 or overs_faced > 50:
        raise InputValidationError("team1.overs_faced must be in (0, 50]")

    if wickets_lost is None or not (0 <= wickets_lost <= 10):
        raise InputValidationError("team1.wickets_lost must be between 0 and 10")


def _validate_team2(team2: dict, match_status: str) -> None:
    runs_scored = team2.get("runs_scored")
    overs_faced = team2.get("overs_faced")
    wickets_lost = team2.get("wickets_lost")
    scheduled_overs = team2.get("scheduled_overs")

    if runs_scored is None or runs_scored < 0:
        raise InputValidationError("team2.runs_scored must be >= 0")

    if overs_faced is None or overs_faced < 0:
        raise InputValidationError("team2.overs_faced must be >= 0")

    if scheduled_overs is None or scheduled_overs <= 0 or scheduled_overs > 50:
        raise InputValidationError("team2.scheduled_overs must be in (0, 50]")

    if overs_faced > scheduled_overs:
        raise InputValidationError(
            "team2.overs_faced cannot exceed team2.scheduled_overs"
        )

    if wickets_lost is None or not (0 <= wickets_lost <= 10):
        raise InputValidationError("team2.wickets_lost must be between 0 and 10")

    # Logical consistency
    if match_status == "resumed":
        if overs_faced >= scheduled_overs:
            raise InputValidationError(
                "For resumed matches, team2 must have overs remaining"
            )