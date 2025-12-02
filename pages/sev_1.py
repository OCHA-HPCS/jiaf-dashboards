import streamlit as st

from data import load_sev
from figures import make_choropleth, SEV_DM

iso = st.query_params.get("iso")
if not iso:
    st.error("No country selected.")
    st.stop()

df = load_sev(iso)

# Ensure Severity column exists
if "Severity" not in df.columns and "Final Severity" in df.columns:
    df["Severity"] = df["Final Severity"]

st.subheader("Where are the areas with the highest severity?", divider="blue")

if "Severity" in df.columns:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**:blue-background[Severity] by admin area**")
        df["Severity"] = df["Severity"].dropna(how="all").astype(int).astype(str)
        final_sev_fig = make_choropleth(df, iso, "Severity", "By Admin 2", "Blues", all_categories=["1", "2", "3", "4", "5"],
                                        continuous=False, discrete_map=SEV_DM)
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
else:
    st.error("Severity data not found.")