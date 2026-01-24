import streamlit as st
from pathlib import Path
import sys

# -------- Path setup --------
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT / "src"))

from dls.pipeline import run_dls_pipeline
from dls.errors import InputValidationError

RESOURCE_TABLE_PATH = "data/derived/resource_table_empirical_final.csv"

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
t1_overs = st.number_input("Overs Faced", min_value=0.0, max_value=50.0, step=0.1, key="t1_overs")
t1_wickets = st.number_input("Wickets Lost", min_value=0, max_value=10, step=1, key="t1_wkts")

# ---------- Team 2 ----------
st.header("Team 2 (Second Innings)")
t2_score = st.number_input("Score", min_value=0, step=1, key="t2_score")
t2_overs = st.number_input("Overs Faced", min_value=0.0, max_value=50.0, step=0.1, key="t2_overs")
t2_wickets = st.number_input("Wickets Lost", min_value=0, max_value=10, step=1, key="t2_wkts")
t2_scheduled = st.number_input("Scheduled Overs", min_value=1.0, max_value=50.0, step=0.5, key="t2_sched")

# ---------- Run engine ----------
if st.button("Run DLS Engine"):
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
            "wickets_lost": t1_wickets
        },
        "team2": {
            "runs_scored": t2_score,
            "overs_faced": t2_overs,
            "wickets_lost": t2_wickets,
            "scheduled_overs": t2_scheduled
        }
    }

    try:
        result = run_dls_pipeline(input_data, RESOURCE_TABLE_PATH)

        st.success("DLS Decision Computed")

        decision = result["decision"]

        st.subheader("Decision")
        st.write(f"**Result:** {decision['result']}")

        if "revised_target" in decision:
            st.write(f"**Revised Target:** {decision['revised_target']}")

        if "runs_needed" in decision:
            st.write(f"**Runs Needed:** {decision['runs_needed']}")

    except InputValidationError as e:
        st.error(f"Invalid input: {e}")