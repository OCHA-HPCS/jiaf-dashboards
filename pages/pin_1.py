import seaborn as sns
import streamlit as st

from data import load_df
from figures import make_choropleth

iso = st.query_params.get("iso")
if not iso:
    st.error("No country selected.")
    st.stop()

df = load_df(iso)

cm = sns.light_palette("green", as_cmap=True)

st.subheader("Where is the highest concentration of population in need in the country?", divider="green")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**:green-background[Final PiN] by admin area**")
    final_pin_fig = make_choropleth(df, iso, "Final PiN", "PiN", "Greens", continuous=True)
    st.plotly_chart(final_pin_fig, width="stretch", key="pin2")
with col2:
    df_disp = df[["Admin 1", "Admin 2", "Final PiN", "% PiN"]].sort_values(by="Final PiN",
                                                                           ascending=False).dropna(
        subset=["Final PiN"]).reset_index(drop=True)
    st.markdown(":green-background[**Admin units with highest PiN**]")
    st.dataframe(df_disp.style.background_gradient(cmap=cm, subset=["Final PiN", "% PiN"]),
                 width="stretch", hide_index=True,
                 column_config={
                     "Final PiN": st.column_config.NumberColumn(
                         "Final PiN",
                         format="compact"),
                     "% PiN": st.column_config.NumberColumn(
                         "PiN as % of population",
                         format="percent")
                 })