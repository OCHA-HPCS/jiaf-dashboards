import pandas as pd
import streamlit as st
import yaml
import os
import etl

def get_config(iso):
    if not iso:
        st.error("No country selected.")
        st.stop()
    iso = iso.upper()
    config_path = os.path.join("config", f"{iso}.yaml")
    if not os.path.exists(config_path):
        st.error(f"Configuration for {iso} not found.")
        st.stop()
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_sectors(iso):
    config = get_config(iso)
    return config.get('sectors', [])

@st.cache_data(ttl=3600)
def load_raw_data(iso, sheet_name):
    config = get_config(iso)
    file_path = config['file_path']
    # Load only the requested sheet
    return pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine="calamine")

@st.cache_data(ttl=3600)
def load_df(iso):
    # Check for precomputed
    precomputed_path = os.path.join("precomputed", iso, "pin.parquet")
    if os.path.exists(precomputed_path):
        return pd.read_parquet(precomputed_path)

    # Load config and data
    config = get_config(iso)
    sheet_name = config['sheets']['pin']
    df = load_raw_data(iso, sheet_name).copy()
    
    return etl.process_pin_data(config, df)

@st.cache_data(ttl=3600)
def load_hist(iso):
    # Check for precomputed
    precomputed_path = os.path.join("precomputed", iso, "hist.parquet")
    if os.path.exists(precomputed_path):
        return pd.read_parquet(precomputed_path)

    config = get_config(iso)
    sheet_name = config['sheets']['history']
    hist_df = load_raw_data(iso, sheet_name).copy()
    
    return etl.process_hist_data(config, hist_df)

@st.cache_data(ttl=3600)
def load_sev(iso):
    # Check for precomputed
    precomputed_path = os.path.join("precomputed", iso, "sev.parquet")
    if os.path.exists(precomputed_path):
        return pd.read_parquet(precomputed_path)

    config = get_config(iso)
    sheet_name = config['sheets']['severity']
    sev_df = load_raw_data(iso, sheet_name).copy()
    
    return etl.process_sev_data(config, sev_df)