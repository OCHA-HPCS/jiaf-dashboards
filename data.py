import pandas as pd
import streamlit as st

sectors = ["CCCM", "Education", "Nutrition", "Food Security", "Health", "Overarching Protection",
           "Shelter", "WASH"]


@st.cache_data(ttl=3600)
def load_raw_data():
    sheet_names = ['WS - 3.1 Overall PiN', 'PiN Historical Trend', 'WS - 3.2 Intersectoral Severity']
    return pd.read_excel("MOZ_Worksheet_3A_3B_PiN_Sev_V4_2026_1_original.xlsx", sheet_name=sheet_names, header=None, engine="calamine")


@st.cache_data(ttl=3600)
def load_df():
    raw_data = load_raw_data()
    df = raw_data['WS - 3.1 Overall PiN'].copy()
    # Original code used header=0 (default), so Row 0 was header.
    # Then df.columns = df.iloc[1] (Row 2).
    # Then df.drop([0, 1]).
    # With header=None:
    # Row 0 -> Index 0
    # Row 1 -> Index 1
    # Row 2 -> Index 2 (This is the header)
    df.columns = df.iloc[2]
    df = df.iloc[3:].reset_index(drop=True)
    
    df["Final PiN"] = pd.to_numeric(df["Final PiN"], errors='coerce', downcast="integer")
    df["% PiN"] = df["Final PiN"] / df["Population"]
    for sector in sectors:
        df[sector] = pd.to_numeric(df[sector], errors='coerce')
    return df


@st.cache_data(ttl=3600)
def load_hist():
    raw_data = load_raw_data()
    hist_df = raw_data['PiN Historical Trend'].copy()
    # Original used header=2 (Row 2).
    # With header=None, Row 2 is Index 2.
    hist_df.columns = hist_df.iloc[2]
    hist_df = hist_df.iloc[3:].reset_index(drop=True)
    
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
    raw_data = load_raw_data()
    sev_df = raw_data['WS - 3.2 Intersectoral Severity'].copy()
    # Original used header=2 (Row 2).
    sev_df.columns = sev_df.iloc[2]
    sev_df = sev_df.iloc[3:].reset_index(drop=True)
    
    for s in sectors:
        sev_df[s] = pd.to_numeric(sev_df[s], errors='coerce')
    return sev_df
