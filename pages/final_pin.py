import streamlit as st

from data import load_df, load_sev, get_config
from figures import make_choropleth, SEV_DM

iso = st.query_params.get("iso")
if not iso:
    st.error("No country selected.")
    st.stop()

df = load_df(iso)
sev_df = load_sev(iso)
config = get_config(iso)
pcode_col = config.get('geo', {}).get('pcode_col', "Admin 2 P-Code")

# Merge Severity if not present
if "Severity" not in df.columns:
    # Try to find severity column in sev_df
    sev_col = "Final Severity"
    if sev_col not in sev_df.columns:
        # Fallback or check mapping
        # If mapped, it should be there. If not, maybe it's "Severity"?
        if "Severity" in sev_df.columns:
            sev_col = "Severity"
            
    if sev_col in sev_df.columns and pcode_col in df.columns and pcode_col in sev_df.columns:
        # Merge only the severity column
        df = df.merge(sev_df[[pcode_col, sev_col]], on=pcode_col, how="left")
        df["Severity"] = df[sev_col]

if "Severity" not in df.columns:
    st.error("Severity data not found.")
else:
    st.subheader("Where is the highest concentration of population in need in the country?", divider="rainbow")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**:green-background[Final PiN] by admin area**")
        fig = make_choropleth(df, iso, "Final PiN", "Final PiN", "Greens", continuous=True)
        st.plotly_chart(fig, width="stretch")
    with col2:
        st.markdown("**:blue-background[Final Severity] by admin area**")
        df["Severity"] = df["Severity"].dropna(how="all").astype(int).astype(str)
        fig = make_choropleth(df, iso, "Severity", "Final Severity", "Blues", all_categories=["1", "2", "3", "4", "5"],
                              discrete_map=SEV_DM,
                              continuous=False)
        st.plotly_chart(fig, width="stretch")