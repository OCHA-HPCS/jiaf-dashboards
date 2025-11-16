import plotly.express as px
import streamlit as st

from data import load_df, sectors

df = load_df()

st.subheader("Which sectors have the highest PiN?", divider="green")

sector_tm_df = df[sectors].sum().reset_index()
sector_tm_df.columns = ["Sector", "Total PiN"]

admin_sector_df = df[["Admin 1", "Admin 2"]].copy()
admin_sector_df["Highest Sector"] = df[sectors].idxmax(axis=1)
admin_sector_df["Highest Sector PiN"] = df[sectors].max(axis=1)
admin_sector_df["Second Highest Sector"] = df[sectors].apply(lambda x: x.nlargest(2).idxmin(), axis=1)
admin_sector_df["Second Highest Sector PiN"] = df[sectors].apply(lambda x: x.nlargest(2).min(), axis=1)
admin_sector_df.drop(["Highest Sector PiN", "Second Highest Sector PiN"], axis=1, inplace=True)
admin_sector_df.dropna(subset=["Highest Sector"], axis=0, inplace=True)

admin_highest_df = admin_sector_df["Highest Sector"].value_counts().reset_index()
admin_highest_df.columns = ["Sector", "Number of Areas as Highest PiN Sector"]

col1, col2 = st.columns(2)

with col1:
    st.markdown("**:green-background[Total Sectoral PiN Distribution]**")
    fig = px.treemap(sector_tm_df, path=[px.Constant("Total Sectoral PiN"), 'Sector'], values='Total PiN',
                     color="Total PiN", color_continuous_scale='Greens', parents=None)
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
    st.plotly_chart(fig)

    st.markdown("**:green-background[Final PiN] by admin area**")
    fig = px.bar(admin_highest_df, x='Sector', y='Number of Areas as Highest PiN Sector',
                 color='Number of Areas as Highest PiN Sector',
                 color_continuous_scale='Greens')
    fig.update_layout(xaxis_title='Sector', yaxis_title='Number of Areas', margin=dict(t=0, l=0, r=0, b=0))
    st.plotly_chart(fig)
with col2:
    st.markdown("**:green-background[Highest PiN sectors] by admin area**")
    st.dataframe(admin_sector_df, hide_index=True)
