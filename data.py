import pandas as pd
import streamlit as st

sectors = ["CCCM", "Education", "Nutrition", "Food Security", "Health", "Overarching Protection",
           "Shelter", "WASH"]


@st.cache_data(ttl=3600)
def load_df():
    df = pd.read_excel("MOZ_Worksheet_3A_3B_PiN_Sev_V4_2026_1_original.xlsx", sheet_name=2)
    df.columns = df.iloc[1]
    df.drop([0, 1], inplace=True)
    df["Final PiN"] = pd.to_numeric(df["Final PiN"], errors='coerce', downcast="integer")
    df["% PiN"] = df["Final PiN"] / df["Population"]
    for sector in sectors:
        df[sector] = pd.to_numeric(df[sector], errors='coerce')
    return df


@st.cache_data(ttl=3600)
def load_hist():
    hist_df = pd.read_excel("MOZ_Worksheet_3A_3B_PiN_Sev_V4_2026_1_original.xlsx", sheet_name=3, header=2)
    sectors_old = [f"{sector} - old" for sector in sectors]
    sectors_new = [f"{sector} - new" for sector in sectors]
    for old, new in zip(sectors_old, sectors_new):
        hist_df[old] = pd.to_numeric(hist_df[old], errors='coerce')
        hist_df[new] = pd.to_numeric(hist_df[new], errors='coerce')
    hist_df["PiN Delta"] = hist_df[sectors_new].sum(axis=1) - hist_df[sectors_old].sum(axis=1)
    hist_df["PiN Delta %"] = hist_df["PiN Delta"] / hist_df[sectors_old].sum(axis=1).replace({0: pd.NA})
    hist_df["Old PiN"] = hist_df[sectors_old].sum(axis=1)
    hist_df["New PiN"] = hist_df[sectors_new].sum(axis=1)
    return hist_df


@st.cache_data(ttl=3600)
def load_sev():
    sev_df = pd.read_excel("MOZ_Worksheet_3A_3B_PiN_Sev_V4_2026_1_original.xlsx", sheet_name=5, header=2)
    for s in sectors:
        sev_df[s] = pd.to_numeric(sev_df[s], errors='coerce')
    return sev_df
