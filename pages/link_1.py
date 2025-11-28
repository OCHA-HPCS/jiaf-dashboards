import streamlit as st

from data import load_df
from figures import make_choropleth

df = load_df()

st.subheader("Which areas have both high PiN and high Severity?", divider="violet")
with st.container(border=1):
    pin_threshold = st.slider("% of population in need", 0, 100, 60) / 100
    sev_threshold = st.slider("Severity threshold", 0, 5, 4)

overlap_df = df[["Admin 1", "Admin 2", "Admin 2 P-Code", "% PiN", "Severity"]].copy()


def categorize_area(row):
    pin_high = row["% PiN"] >= pin_threshold
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
    st.markdown("**:violet-background[Areas exceeding thresholds]**")
    display_df = overlap_df[overlap_df["Category"] != "None"][["Admin 1", "Admin 2", "% PiN", "Severity"]]
    display_df.dropna(subset=["% PiN", "Severity"], axis=0, inplace=True)
    display_df["Severity"] = display_df["Severity"].astype(int)
    display_df = display_df[
        (display_df["% PiN"] >= pin_threshold) & (display_df["Severity"] >= sev_threshold)
        ].sort_values(by=["% PiN", "Severity"], ascending=False).reset_index(drop=True)
    st.dataframe(display_df.style.background_gradient(
        subset=["% PiN"], cmap="Greens"
    ).background_gradient(
        subset=["Severity"], cmap="Blues"
    ), hide_index=True, column_config={
        "% PiN": st.column_config.NumberColumn(
            "% PiN",
            format="percent",
        ),
    })
