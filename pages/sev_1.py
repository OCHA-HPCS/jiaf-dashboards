import streamlit as st

from data import load_df
from figures import make_choropleth

df = load_df()

st.subheader("Where are the areas with the highest severity?", divider="blue")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**:blue-background[Severity] by admin area**")
    final_sev_fig = make_choropleth(df, "Severity", "By Admin 2", "Blues")
    st.plotly_chart(final_sev_fig, width="stretch", key="sev2")
with col2:
    df_disp = df[["Admin 1", "Admin 2", "Severity"]].sort_values(by="Severity",
                                                                 ascending=False).dropna(
        subset=["Severity"]).reset_index(drop=True)
    st.markdown(":blue-background[**Admin units with highest Severity**]")
    st.dataframe(df_disp.style.background_gradient(cmap="Blues", subset=["Severity"]),
                 width="stretch", hide_index=True,
                 column_config={
                     "Severity": st.column_config.NumberColumn(
                         "Severity",
                         format="compact")
                 })
