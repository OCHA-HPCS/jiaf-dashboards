import streamlit as st

from data import get_sectors, load_sev
from figures import make_choropleth

iso = st.query_params.get("iso")
if not iso:
    st.error("No country selected.")
    st.stop()

sev_df = load_sev(iso)
all_sectors = get_sectors(iso)
sectors = [s for s in all_sectors if s in sev_df.columns]

st.subheader("Which areas have a large number of sectors with high severity of needs?", divider="blue")
with st.container(border=1):
    threshold = st.slider("Severity threshold", 0, 5, 3)

col1, col2 = st.columns(2)
with col1:
    if sectors:
        sev_df["Sectors above severity threshold"] = sev_df[sectors].gt(threshold).sum(axis=1)
        sev_df_filtered = sev_df[sev_df["Sectors above severity threshold"] > 0]
        st.markdown("**:blue-background[Number of sectors above severity threshold]**")
        fig = make_choropleth(sev_df_filtered, iso, "Sectors above severity threshold"
                              , "Sectors",
                              "Reds")
        st.plotly_chart(fig, width="stretch")
    else:
        st.warning("No sector data found.")
        
with col2:
    if "Sectors above severity threshold" in sev_df.columns:
        df_disp = sev_df[["Admin 1", "Admin 2", "Final Severity", "Sectors above severity threshold"]].sort_values(
            by="Sectors above severity threshold", ascending=False).dropna(subset=["Final Severity"]).reset_index(drop=True)
        st.markdown(":blue-background[**Admin units with highest number of sectors above severity threshold**]")
        st.dataframe(df_disp.style.background_gradient(cmap="Blues", subset=["Final Severity"]).background_gradient(
            cmap="Reds", subset=["Sectors above severity threshold"]),
            width="stretch", hide_index=True,
            column_config={
                "Final Severity": st.column_config.NumberColumn(
                    "Final Severity",
                    format="compact"),
            })