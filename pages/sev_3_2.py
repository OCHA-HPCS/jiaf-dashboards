import plotly.express as px
import streamlit as st

from data import load_sev, sectors

sev_df = load_sev()

st.subheader("Which sectors have the highest severity?", divider="blue")

sector_sev_df = sev_df[sectors].melt(var_name="Sector", value_name="Severity")
sector_sev_counts = sector_sev_df.groupby(["Sector", "Severity"]).size().reset_index(name="Count")
sector_sev_counts = sector_sev_counts[sector_sev_counts["Severity"] > 0]

col1, col2 = st.columns(2)
with col1:
    st.markdown("**:blue-background[Number of areas by sector and severity level]**")
    fig = px.bar(sector_sev_counts, x='Sector', y='Count', color='Severity',
                 color_continuous_scale='Blues')
    fig.update_layout(xaxis_title='Sector', yaxis_title='Number of Areas', margin=dict(t=30, l=0, r=0, b=0))
    st.plotly_chart(fig)
with col2:
    # dataframe with admin 1, admin 2, names of sectors at phase 5 and names of sectors at phase 4
    sector_high_df = sev_df[["Admin 1", "Admin 2"]].copy()
    sector_high_df["Sectors at Phase 5"] = sev_df[sectors].apply(
        lambda x: ', '.join(x.index[x == 5].tolist()) if any(x == 5) else None, axis=1)
    sector_high_df["Sectors at Phase 4"] = sev_df[sectors].apply(
        lambda x: ', '.join(x.index[x == 4].tolist()) if any(x == 4) else None, axis=1)
    sector_high_df = sector_high_df.dropna(subset=["Sectors at Phase 5", "Sectors at Phase 4"], how='all').reset_index(
        drop=True)
    st.markdown("**:blue-background[Areas with sectors at Phase 4 and 5]**")
    st.dataframe(sector_high_df, hide_index=True)
