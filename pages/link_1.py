import streamlit as st

from data import df
from figures import make_choropleth

st.subheader("Which areas have both high PiN and high Severity?", divider="violet")
with st.container(border=1):
    c1, c2 = st.columns(2)
    with c1:
        pin_threshold = st.slider("PiN threshold", 0, 100, 70)
    with c2:
        sev_threshold = st.slider("Severity threshold", 0, 5, 3)

# Dataframe with areas -> "Both" if PiN and Severity exceed thresholds, "PiN Only" if only PiN exceeds, "Severity Only" if only Severity exceeds, else "None"
overlap_df = df[["Admin 2", "Admin 2 P-Code", "Final PiN", "Severity"]].copy()


def categorize_area(row):
    pin_high = row["Final PiN"] >= pin_threshold
    sev_high = row["Severity"] >= sev_threshold
    if pin_high and sev_high:
        return "Both"
    elif pin_high:
        return "PiN Only"
    elif sev_high:
        return "Severity Only"
    else:
        return "None"


overlap_df["Category"] = overlap_df.apply(categorize_area, axis=1)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**:violet-background[Overlap of overall PiN and intersectoral severity]**")
    fig = make_choropleth(overlap_df, "Category", "Category", "Purples", discrete_map={
        "Both": "darkviolet",
        "PiN Only": "mediumpurple",
        "Severity Only": "plum",
        "None": "lavender"
    })
    st.plotly_chart(fig, width="stretch")
with col2:
    # Table with admin 1, admin 2, Final PiN, Severity for areas where Category is not "None"
    st.markdown("**:violet-background[Areas exceeding thresholds]**")
    display_df = overlap_df[overlap_df["Category"] != "None"][["Admin 2", "Final PiN", "Severity"]]
    display_df.dropna(subset=["Final PiN", "Severity"], axis=0, inplace=True)
    st.dataframe(display_df.style.background_gradient(
        subset=["Final PiN"], cmap="Greens"
    ).background_gradient(
        subset=["Severity"], cmap="Blues"
    ), hide_index=True, column_config={
        "Final PiN": st.column_config.NumberColumn(
            "Final PiN",
            format="compact",
        ),
        "Severity": st.column_config.NumberColumn(
            "Severity",
            format="compact",
        ),
    })
