import streamlit as st

from data import df
from figures import make_choropleth

st.subheader("Where is the highest concentration of population in need in the country?", divider="rainbow")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**:green-background[Final PiN] by admin area**")
    fig = make_choropleth(df, "Final PiN", "Final PiN", "Greens")
    st.plotly_chart(fig, width="stretch")
with col2:
    st.markdown("**:blue-background[Final Severity] by admin area**")
    fig = make_choropleth(df, "Severity", "Final Severity", "Reds")
    st.plotly_chart(fig, width="stretch")
