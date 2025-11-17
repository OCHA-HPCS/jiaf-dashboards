import seaborn as sns
import streamlit as st

from data import load_df, sectors
from figures import make_choropleth

df = load_df()

cm = sns.light_palette("green", as_cmap=True)

st.subheader("Which areas have a large number of sectors with a large PiN?", divider="green")
with st.container(border=1):
    threshold = st.slider("% of population in need", 0, 100, 75)
col1, col2 = st.columns(2)
with col1:
    st.markdown(":green-background[**Number of sectors above PiN threshold**]")
    df["Sectors above threshold"] = df[[f"{s}%" for s in sectors]].gt(threshold / 100).sum(axis=1)
    fig = make_choropleth(df, "Sectors above threshold", "Sectors", "Greens")
    st.plotly_chart(fig, width="stretch")
with col2:
    df_disp = df[["Admin 1", "Admin 2", "Final PiN", "Sectors above threshold"]].sort_values(
        by="Sectors above threshold", ascending=False).dropna(subset=["Final PiN"]).reset_index(drop=True)
    st.markdown(":green-background[**Admin units with highest number of sectors above PiN threshold**]")
    st.dataframe(df_disp.style.background_gradient(cmap=cm, subset=["Final PiN", "Sectors above threshold"]),
                 width="stretch", hide_index=True,
                 column_config={
                     "Final PiN": st.column_config.NumberColumn(
                         "Final PiN",
                         format="compact"),
                 })
