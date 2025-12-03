import seaborn as sns
import streamlit as st
import pandas as pd

from data import load_df, get_sectors
from figures import make_choropleth

iso = st.query_params.get("iso")
if not iso:
    st.error("No country selected.")
    st.stop()

df = load_df(iso)
sectors = get_sectors(iso)

cm = sns.light_palette("green", as_cmap=True)

st.subheader("Which areas have a large number of sectors with a large PiN?", divider="green")
with st.container(border=1):
    threshold = st.slider("% of population in need", 0, 100, 75)
col1, col2 = st.columns(2)
with col1:
    st.markdown(":green-background[**Number of sectors above PiN threshold**]")
    # Calculate sector percentages dynamically
    valid_sectors = []
    if "Population" in df.columns:
        for s in sectors:
            if s in df.columns:
                pct_col = f"{s}%"
                # Calculate percentage (handle division by zero)
                df[pct_col] = df[s] / df["Population"].replace({0: pd.NA})
                valid_sectors.append(s)

    # Count sectors exceeding threshold
    df["Sectors above threshold"] = df[[f"{s}%" for s in valid_sectors]].gt(threshold / 100).sum(axis=1)
    
    fig = make_choropleth(df, iso, "Sectors above threshold", "Sectors", "Greens", continuous=True)
    st.plotly_chart(fig, width="stretch")
with col2:
    df_disp = df[["Admin 1", "Admin 2", "Final PiN", "Sectors above threshold"]].sort_values(
        by="Sectors above threshold", ascending=False).dropna(subset=["Final PiN"]).reset_index(drop=True)
    st.markdown(":green-background[**Admin units with highest number of sectors above PiN threshold**]")
    st.dataframe(df_disp.style.background_gradient(cmap=cm, subset=["Final PiN", "Sectors above threshold"]),
                 width="stretch", hide_index=True,
                 column_config={
                     "Final PiN": st.column_config.NumberColumn(
                         "Final PiN",
                         format="compact"),
                 })