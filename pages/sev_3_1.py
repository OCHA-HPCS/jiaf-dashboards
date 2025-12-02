import streamlit as st

from data import load_sev, get_sectors
from figures import make_choropleth, SEV_DM

iso = st.query_params.get("iso")
if not iso:
    st.error("No country selected.")
    st.stop()

sev_df = load_sev(iso)
sectors = get_sectors(iso)

st.subheader("Which sectors have the highest severity?", divider="blue")
columns = st.columns(3, gap="small")
for i, sector in enumerate(sectors):
    with columns[i % 3]:
        st.markdown(f"**:blue-background[{sector}] Severity by admin area**")
        if sector in sev_df.columns:
            sev_df[sector] = sev_df[sector].dropna(how="all").astype(int).astype(str)
            fig = make_choropleth(sev_df, iso, sector, "Severity", "Blues", all_categories=["1", "2", "3", "4", "5"],
                                  discrete_map=SEV_DM,
                                  continuous=False)
            st.plotly_chart(fig, width="stretch")
        else:
            st.warning(f"{sector} data not found.")