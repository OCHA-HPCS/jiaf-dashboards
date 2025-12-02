import streamlit as st

from data import load_df, get_sectors
from figures import make_choropleth

iso = st.query_params.get("iso")
if not iso:
    st.error("No country selected.")
    st.stop()

df = load_df(iso)
sectors = get_sectors(iso)

st.subheader("Which sectors have the highest PiN?", divider="green")
columns = st.columns(3, gap="small")
for i, sector in enumerate(sectors):
    with columns[i % 3]:
        st.markdown(f"**:green-background[{sector}] PiN by admin area**")
        # Check if sector column exists
        if sector in df.columns:
            fig = make_choropleth(df, iso, sector, "PiN", "Greens", continuous=True)
            st.plotly_chart(fig, width="stretch")
        else:
            st.warning(f"Data for {sector} not found.")