import streamlit as st

from data import sev_df, sectors
from figures import make_choropleth

st.subheader("Which sectors have the highest severity?", divider="blue")
columns = st.columns(3, gap=None)
for i, sector in enumerate(sectors):
    with columns[i % 3]:
        st.markdown(f"**:blue-background[{sector}] Severity by admin area**")
        fig = make_choropleth(sev_df, sector, "Severity", "Blues")
        st.plotly_chart(fig, width="stretch")
