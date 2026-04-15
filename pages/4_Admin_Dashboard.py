import pandas as pd
import streamlit as st

from services.auth import require_admin, sidebar_login
from services.database import (
    get_admin_stats,
    get_all_claims,
    get_provider_leaderboard,
    get_recent_activity,
)

sidebar_login()
require_admin()

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=15000, key="admin_refresh")
except Exception:
    pass

st.title("Admin Dashboard")
st.caption("Real-time AI fraud monitoring and claim operations center")

stats = get_admin_stats()
claims = pd.DataFrame(get_all_claims())
leaderboard = pd.DataFrame(get_provider_leaderboard())
activity = pd.DataFrame(get_recent_activity())

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Claims", stats["total_claims"])
c2.metric("Pending Review", stats["pending"])
c3.metric("Approved", stats["approved"])
c4.metric("Rejected", stats["rejected"])
c5.metric("High Risk", stats["high_risk"])
c6.metric("Users", stats["total_users"])

if claims.empty:
    st.info("No claims available yet.")
    st.stop()

row1_left, row1_right = st.columns(2)
with row1_left:
    st.subheader("Claims by Status")
    st.bar_chart(claims["workflow_status"].value_counts())

with row1_right:
    st.subheader("Claims by Risk Level")
    st.bar_chart(claims["risk_level"].value_counts())

row2_left, row2_right = st.columns([1.1, 1])

with row2_left:
    st.subheader("Provider Leaderboard")
    st.dataframe(
        leaderboard,
        use_container_width=True,
        hide_index=True,
    )

with row2_right:
    st.subheader("Recent Activity Feed")
    if activity.empty:
        st.info("No activity yet.")
    else:
        for _, item in activity.iterrows():
            st.markdown(
                f"**{item['event_title']}**  \n"
                f"{item['full_name']} • {item['provider_name']}  \n"
                f"{item['event_description'] or ''}  \n"
                f"`{item['created_at']}`"
            )
            st.markdown("---")

st.subheader("Recent Claims")
recent = claims[
    ["id", "full_name", "hospital_name", "provider_name", "claim_amount", "risk_level", "workflow_status", "submitted_at"]
].head(10)
st.dataframe(recent, use_container_width=True, hide_index=True)

if st.button("Refresh Dashboard"):
    st.rerun()