import streamlit as st

from data import sectors, load_sev
from figures import make_choropleth

sev_df = load_sev()

st.subheader("Which areas have a large number of sectors with high severity of needs?", divider="blue")
with st.container(border=1):
    threshold = st.slider("Severity threshold", 0, 5, 3)

col1, col2 = st.columns(2)
with col1:
    sev_df["Sectors above severity threshold"] = sev_df[sectors].gt(threshold).sum(axis=1)
    sev_df = sev_df[sev_df["Sectors above severity threshold"] > 0]
    st.markdown("**:blue-background[Number of sectors above severity threshold]**")
    fig = make_choropleth(sev_df, "Sectors above severity threshold"
                          , "Sectors",
                          "Blues")
    st.plotly_chart(fig, width="stretch")
with col2:
    df_disp = sev_df[["Admin 1", "Admin 2", "Final Severity", "Sectors above severity threshold"]].sort_values(
        by="Sectors above severity threshold", ascending=False).dropna(subset=["Final Severity"]).reset_index(drop=True)
    st.markdown(":blue-background[**Admin units with highest number of sectors above severity threshold**]")
    st.dataframe(df_disp.style.background_gradient(cmap="Blues", subset=["Final Severity",
                                                                         "Sectors above severity threshold"]),
                 width="stretch", hide_index=True,
                 column_config={
                     "Final Severity": st.column_config.NumberColumn(
                         "Final Severity",
                         format="compact"),
                 })
