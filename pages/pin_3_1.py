import streamlit as st

from data import load_df, sectors
from figures import make_choropleth

df = load_df()

st.subheader("Which sectors have the highest PiN?", divider="green")
columns = st.columns(3, gap=None)
for i, sector in enumerate(sectors):
    with columns[i % 3]:
        st.markdown(f"**:green-background[{sector}] PiN by admin area**")
        fig = make_choropleth(df, sector, "PiN", "Greens")
        st.plotly_chart(fig, width="stretch")
