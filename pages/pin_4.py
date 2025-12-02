import streamlit as st
import pandas as pd

from data import load_hist, get_sectors
from figures import make_choropleth

iso = st.query_params.get("iso")
if not iso:
    st.error("No country selected.")
    st.stop()

hist_df = load_hist(iso)
sectors = get_sectors(iso)

st.subheader("What is the PiN trend as compared to the previous year?", divider="green")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**:green-background[Overall PiN change] by admin area**")
    fig = make_choropleth(hist_df, iso, "PiN Delta", "PiN Change",
                          "Temps", continuous=True)
    st.plotly_chart(fig, width="stretch")

    if sectors:
        # Calculate % change per sector manually
        df_pct_change = hist_df[["Admin 1", "Admin 2"]].copy()
        display_sectors = []
        for sector in sectors:
            old_col = f"{sector} - old"
            new_col = f"{sector} - new"
            if old_col in hist_df.columns and new_col in hist_df.columns:
                # Calculate % change: (New - Old) / Old
                # Handle potential division by zero or NaNs
                diff = hist_df[new_col] - hist_df[old_col]
                df_pct_change[sector] = diff / hist_df[old_col].replace({0: pd.NA})
                display_sectors.append(sector)
        
        if display_sectors:
            st.markdown(":green-background[**Percentage change in PiN by sector**]")
            st.dataframe(df_pct_change.style.background_gradient(cmap="RdYlGn_r", subset=display_sectors), width="stretch",
                         hide_index=True,
                         column_config={s: st.column_config.NumberColumn(
                             s,
                             format="percent") for s in display_sectors})
        else:
             st.info("No paired historical data found for sectors.")
    else:
        st.info("No sector percentage change data available.")

with col2:
    # Ensure columns exist
    cols_needed = ["Admin 1", "Admin 2", "PiN Delta", "Old PiN", "New PiN", "PiN Delta %"]
    available_cols = [c for c in cols_needed if c in hist_df.columns]
    
    if "PiN Delta" in available_cols:
        df_hist_disp = hist_df[available_cols].sort_values(
            by="PiN Delta", ascending=False).dropna(subset=["PiN Delta"]).reset_index(drop=True)
        st.markdown(":green-background[**Admin units with highest PiN change %**]")
        st.dataframe(df_hist_disp.style.background_gradient(cmap="RdYlGn_r", subset=["PiN Delta"]),
                     width="stretch", hide_index=True,
                     column_config={
                         "PiN Delta": st.column_config.NumberColumn(
                             "PiN Delta",
                             format="compact"),
                         "Old PiN": st.column_config.NumberColumn(
                             "Old PiN",
                             format="compact"),
                         "New PiN": st.column_config.NumberColumn(
                             "New PiN",
                             format="compact"),
                         "PiN Delta %": st.column_config.NumberColumn(
                             "% Change",
                             format="percent"),
                     })