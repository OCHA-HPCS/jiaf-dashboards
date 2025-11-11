import streamlit as st

from data import df, sectors

st.subheader("To what extent do sectoral PiNs cross-correlate?", divider="violet")

xc_df = df[sectors].corr()
xc_df.index.name = "Sector"
for sector in sectors:
    xc_df.at[sector, sector] = None

with st.container(border=1):
    threshold = st.slider("Correlation coefficient threshold", 0, 100, 50) / 100

col1, col2 = st.columns(2)
with col1:
    st.markdown("**:violet-background[Correlation coefficient for PiN between sectors]**")
    st.dataframe(xc_df.style.background_gradient(
        cmap="Purples"
    ), width="stretch", column_config={
        sector: st.column_config.NumberColumn(
            sector,
            format="percent",
        ) for sector in sectors
    })
with col2:
    st.markdown("**:violet-background[List of sector correlations with a coefficient greater than the threshold]**")
    sector_sector_cor_df = xc_df.stack().reset_index()
    sector_sector_cor_df.columns = ["Sector 1", "Sector 2", "Correlation Coefficient"]
    sector_sector_cor_df.dropna(subset=["Correlation Coefficient"], axis=0, inplace=True)
    sector_sector_cor_df = sector_sector_cor_df[sector_sector_cor_df["Correlation Coefficient"] >= threshold]
    sector_sector_cor_df = sector_sector_cor_df.sort_values(by="Correlation Coefficient", ascending=False).reset_index(
        drop=True)
    st.dataframe(sector_sector_cor_df.style.background_gradient(
        subset=["Correlation Coefficient"], cmap="Purples"
    ), hide_index=True, width="stretch", column_config={
        "Correlation Coefficient": st.column_config.NumberColumn(
            "Correlation Coefficient",
            format="percent",
        )
    })
