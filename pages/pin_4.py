import streamlit as st

from data import hist_df, sectors
from figures import make_choropleth

st.subheader("What is the PiN trend as compared to the previous year?", divider="green")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**:green-background[Overall PiN change] by admin area**")
    fig = make_choropleth(hist_df, "PiN Delta", "PiN Change",
                          "Temps")
    st.plotly_chart(fig, width="stretch")

    df_pct_change = hist_df[["Admin 1", "Admin 2"] + sectors]
    df_pct_change.dropna(inplace=True)
    st.markdown(":green-background[**Percentage change in PiN by sector**]")
    st.dataframe(df_pct_change.style.background_gradient(cmap="RdYlGn_r", subset=sectors), width="stretch",
                 hide_index=True,
                 column_config={s: st.column_config.NumberColumn(
                     s,
                     format="percent") for s in sectors})
with col2:
    df_hist_disp = hist_df[["Admin 1", "Admin 2", "PiN Delta %", "Old PiN", "New PiN"]].sort_values(
        by="PiN Delta %", ascending=False).dropna(subset=["PiN Delta %"]).reset_index(drop=True)
    st.markdown(":green-background[**Admin units with highest PiN change %**]")
    st.dataframe(df_hist_disp.style.background_gradient(cmap="RdYlGn_r", subset=["PiN Delta %"]),
                 width="stretch", hide_index=True,
                 column_config={
                     "PiN Delta %": st.column_config.NumberColumn(
                         "PiN Delta",
                         format="percent"),
                     "Old PiN": st.column_config.NumberColumn(
                         "Old PiN",
                         format="compact"),
                     "New PiN": st.column_config.NumberColumn(
                         "New PiN",
                         format="compact"),
                 })
