import pandas as pd
import streamlit as st

from data import load_df, load_sev, get_config
from figures import make_choropleth

iso = st.query_params.get("iso")
if not iso:
    st.error("No country selected.")
    st.stop()

df = load_df(iso)
sev_df = load_sev(iso)
config = get_config(iso)
pcode_col = config.get('geo', {}).get('pcode_col', "Admin 2 P-Code")

# Merge Severity if not present
if "Severity" not in df.columns:
    # Try to find severity column in sev_df
    sev_col = "Final Severity"
    if sev_col not in sev_df.columns:
        if "Severity" in sev_df.columns:
            sev_col = "Severity"
            
    if sev_col in sev_df.columns and pcode_col in df.columns and pcode_col in sev_df.columns:
        # Merge only the severity column
        df = df.merge(sev_df[[pcode_col, sev_col]], on=pcode_col, how="left")
        df["Severity"] = df[sev_col]

st.subheader("Which areas have both high PiN and high Severity?", divider="violet")
with st.container(border=1):
    pin_threshold = st.slider("% of population in need", 0, 100, 60) / 100
    sev_threshold = st.slider("Severity threshold", 0, 5, 4)

agg_df = df.copy()
if "Severity" in agg_df.columns:
    agg_df["Severity"] = pd.to_numeric(agg_df["Severity"], errors='coerce')
else:
    st.error("Severity data not found.")
    st.stop()

# Grouping columns: We need to be careful if columns differ.
# For now, we assume Admin 1, Admin 2, and the P-Code column exist.
# The P-Code column name is usually "Admin 2 P-Code" but could vary.
# For grouping, we should probably use columns that identify the area.
# We'll assume the default columns exist for now, as per MOZ.
group_cols = ["Admin 1", "Admin 2"]
# Check for P-Code column
if pcode_col in df.columns:
    group_cols.append(pcode_col)

overlap_df = agg_df.groupby(group_cols, as_index=False).agg({
    "Final PiN": "sum",
    "Population": "sum",
    "Severity": "max"
})
overlap_df["% PiN"] = overlap_df["Final PiN"] / overlap_df["Population"]


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
    fig = make_choropleth(overlap_df, iso, "Category", "Category", "Purples", discrete_map={
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