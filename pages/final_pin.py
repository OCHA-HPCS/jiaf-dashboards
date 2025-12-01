import streamlit as st

from data import load_df
from figures import make_choropleth, SEV_DM

df = load_df()

st.subheader("Where is the highest concentration of population in need in the country?", divider="rainbow")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**:green-background[Final PiN] by admin area**")
    fig = make_choropleth(df, "Final PiN", "Final PiN", "Greens", continuous=True)
    st.plotly_chart(fig, width="stretch")
with col2:
    st.markdown("**:blue-background[Final Severity] by admin area**")
    df["Severity"] = df["Severity"].dropna(how="all").astype(int).astype(str)
    fig = make_choropleth(df, "Severity", "Final Severity", "Blues", all_categories=["1", "2", "3", "4", "5"],
                          discrete_map=SEV_DM,
                          continuous=False)
    st.plotly_chart(fig, width="stretch")
