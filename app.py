import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import altair as alt

# -------- Path setup --------
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT / "src"))

from dls.pipeline import run_dls_pipeline
from dls.errors import InputValidationError
from dls.engine import DLSEngine
from dls.resource_table import ResourceTable
from dls.engine import bucket_overs

RESOURCE_TABLE_PATH = "data/derived/resource_table_empirical_final.csv"

# -------- Page config --------
st.set_page_config(page_title="DLS Engine Demo", layout="centered")
st.title("🏏 DLS Engine Demo")

st.markdown(
    """
This app demonstrates a **Duckworth–Lewis–Stern (DLS) engine**
built using empirical data from **3079 ODI matches**.
"""
)

# ---------- Match status ----------
st.header("Match Status")
match_status = st.selectbox("Select match status", ["resumed", "abandoned"])

# ---------- Team 1 ----------
st.header("Team 1 (First Innings)")
t1_score = st.number_input("Score", min_value=0, step=1, key="t1_score")
t1_overs = st.number_input(
    "Overs Faced", min_value=0.1, max_value=50.0, step=0.1, value=50.0, key="t1_overs"
)
t1_wickets = st.number_input(
    "Wickets Lost", min_value=0, max_value=10, step=1, key="t1_wkts"
)

# ---------- Team 2 ----------
st.header("Team 2 (Second Innings)")
t2_score = st.number_input("Score", min_value=0, step=1, key="t2_score")
t2_overs = st.number_input(
    "Overs Faced", min_value=0.0, max_value=50.0, step=0.1, value=0.0, key="t2_overs"
)
t2_wickets = st.number_input(
    "Wickets Lost", min_value=0, max_value=10, step=1, key="t2_wkts"
)
t2_scheduled = st.number_input(
    "Scheduled Overs", min_value=1.0, max_value=50.0, step=0.5, key="t2_sched"
)

# ---------- Run engine ----------
if st.button("Run DLS Engine"):
    # ---------- Basic UI validation ----------
    if t1_overs <= 0:
        st.error("Team 1 overs faced must be greater than 0.")
        st.stop()

    if t2_overs < 0:
        st.error("Team 2 overs faced cannot be negative.")
        st.stop()

    if t1_wickets < 0 or t1_wickets > 10:
        st.error("Team 1 wickets must be between 0 and 10.")
        st.stop()

    if t2_wickets < 0 or t2_wickets > 10:
        st.error("Team 2 wickets must be between 0 and 10.")
        st.stop()

    if t2_overs > t2_scheduled:
        st.error(
            "Overs faced by Team 2 cannot exceed scheduled overs. "
            "Please correct the inputs."
        )
        st.stop()

    input_data = {
        "match_status": match_status,
        "team1": {
            "score": t1_score,
            "overs_faced": t1_overs,
            "wickets_lost": t1_wickets,
        },
        "team2": {
            "runs_scored": t2_score,
            "overs_faced": t2_overs,
            "wickets_lost": t2_wickets,
            "scheduled_overs": t2_scheduled,
        },
    }

    try:
        # ---------- Run main DLS pipeline ----------
        result = run_dls_pipeline(input_data, RESOURCE_TABLE_PATH)

        st.success("DLS Decision Computed")

        decision = result["decision"]

        st.subheader("Decision")
        st.write(f"**Result:** {decision['result']}")

        if "revised_target" in decision:
            st.write(f"**Revised Target:** {decision['revised_target']}")

        if "runs_needed" in decision:
            st.write(f"**Runs Needed:** {decision['runs_needed']}")

        # ---------- Step 2: Expected score progression ----------
        # ---------- Step 2: Expected score progression ----------
        if match_status == "resumed":
            st.subheader("📈 Expected Score Progression (No Further Wickets)")
            st.caption("Expected score assuming no further wicket loss.")

            engine = DLSEngine(RESOURCE_TABLE_PATH)

            overs_remaining_now = t2_scheduled - t2_overs
            par_score = result["par_score"]   # ✅ PLACE IT HERE (once)

            future_points = []
            step = 0.5
            o = bucket_overs(overs_remaining_now)

            while o >= 0:
                expected_score = engine.compute_expected_score_at_overs(
                    team2_score=t2_score,
                    par_score=par_score,
                    overs_remaining_now=overs_remaining_now,
                    overs_remaining_future=o,
                    wickets_lost=t2_wickets,
                )

                future_points.append(
                    {
                        "Overs Played": round(t2_scheduled - o, 1),
                        "Expected Score": int(round(expected_score)),
                    }
                )

                o -= step

            df = pd.DataFrame(future_points)
            chart = (
                alt.Chart(df)
                .mark_line(point=True)
                .encode(
                    x=alt.X(
                        "Overs Played:Q",
                        title="Overs Played (Second Innings)"
                    ),
                    y=alt.Y(
                        "Expected Score:Q",
                        title="Expected Team 2 Score"
                    ),
                    tooltip=["Overs Played", "Expected Score"]
                )
            )

            st.altair_chart(chart, use_container_width=True)

    except InputValidationError as e:
        st.error(f"Invalid input: {e}")