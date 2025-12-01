import plotly.express as px
import streamlit as st

from data import load_sev, sectors
from figures import SEV_DM

sev_df = load_sev()

st.subheader("Which sectors have the highest severity?", divider="blue")

sector_sev_df = sev_df[sectors].melt(var_name="Sector", value_name="Severity")
sector_sev_counts = sector_sev_df.groupby(["Sector", "Severity"]).size().reset_index(name="Count")
# sector_sev_counts = sector_sev_counts[sector_sev_counts["Severity"] > 0]
sector_sev_counts['Prop'] = sector_sev_counts.groupby('Sector')['Count'].transform(lambda x: x / x.sum())
sector_sev_counts["Severity"] = sector_sev_counts["Severity"].astype(int).astype(str)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**:blue-background[Proportion of areas by sector and severity level]**")
    cm = SEV_DM
    cm.update(
        {'0': 'lightgrey'}
    )
    fig = px.bar(sector_sev_counts, x='Sector', y='Prop', color='Severity',
                 color_continuous_scale='Blues', color_discrete_map=cm, category_orders={
            'Severity': ['0', '1', '2', '3', '4', '5']
        }, barmode='relative')
    fig.update_layout(xaxis_title='Sector', yaxis_title='Proportion of Areas', margin=dict(t=0, l=0, r=0, b=0))
    st.plotly_chart(fig)
with col2:
    # dataframe with admin 1, admin 2, names of sectors at phase 5 and names of sectors at phase 4
    sector_high_df = sev_df[["Admin 1", "Admin 2"]].copy()

    def get_sectors_at_severity(row, severity_level):
        return ", ".join([idx for idx, val in row.items() if val == severity_level])

    # Pre-filter the DataFrame to only include sector columns for processing
    sector_data = sev_df[sectors]

    # Apply is still used but the lambda is optimized to a clearer function. 
    # For true vectorization we'd need to broadcast columns, which is complex for string joining.
    # Given the small row count (<200), this is acceptable, but we can optimize the 'apply' slightly.
    
    sector_high_df["Sectors at Phase 5"] = sector_data.apply(get_sectors_at_severity, severity_level=5, axis=1)
    sector_high_df["Sectors at Phase 5"] = sector_high_df["Sectors at Phase 5"].replace("", None)
    
    sector_high_df["Sectors at Phase 4"] = sector_data.apply(get_sectors_at_severity, severity_level=4, axis=1)
    sector_high_df["Sectors at Phase 4"] = sector_high_df["Sectors at Phase 4"].replace("", None)

    sector_high_df = sector_high_df.dropna(subset=["Sectors at Phase 5", "Sectors at Phase 4"], how='all').reset_index(
        drop=True)
    st.markdown("**:blue-background[Areas with sectors at Phase 4 and 5]**")
    st.dataframe(sector_high_df, hide_index=True)
