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
    
    hist_df = etl.process_hist_data(config, hist_df)
    
    # Ensure invalid P-Codes are dropped (Fix for outliers with missing geo)
    pcode_col = config.get('geo', {}).get('pcode_col', "Admin 2 P-Code")
    if pcode_col in hist_df.columns:
        hist_df = hist_df.dropna(subset=[pcode_col])

    # Patch for COL: Fill missing "New" data from current PiN
    if iso == "COL" and ("New PiN" not in hist_df.columns or hist_df["New PiN"].sum() == 0):
        try:
            current_df = load_df(iso)
            pcode_col = config['geo']['pcode_col']
            
            # Normalize P-Codes in hist_df to match current_df (e.g. 5001 -> CO05001)
            def fix_pcode(x):
                try:
                    s = str(int(x)).zfill(5)
                    return f"CO{s}"
                except:
                    return str(x)
            
            if pcode_col in hist_df.columns:
                hist_df['matched_pcode'] = hist_df[pcode_col].apply(fix_pcode)
                
                # Merge current data
                merged = pd.merge(hist_df, current_df, left_on='matched_pcode', right_on=pcode_col, suffixes=('', '_curr'), how='left')
                
                # Update sector columns
                sectors = config.get('sectors', [])
                updated_new_cols = []
                updated_old_cols = []
                
                for sector in sectors:
                    new_col = f"{sector} - new"
                    old_col = f"{sector} - old"
                    
                    if sector in current_df.columns:
                        merged[new_col] = merged[sector].fillna(0)
                        
                    if new_col in merged.columns:
                        updated_new_cols.append(new_col)
                    if old_col in merged.columns:
                        updated_old_cols.append(old_col)
                
                # Recalculate Totals
                merged["New PiN"] = merged[updated_new_cols].sum(axis=1)
                merged["Old PiN"] = merged[updated_old_cols].sum(axis=1)
                merged["PiN Delta"] = merged["New PiN"] - merged["Old PiN"]
                merged["PiN Delta %"] = merged["PiN Delta"] / merged["Old PiN"].replace({0: pd.NA})
                
                # Overwrite the original P-Code column with the normalized one for mapping
                merged[pcode_col] = merged['matched_pcode']
                
                # Cleanup
                hist_df = merged
                
        except Exception as e:
            print(f"Failed to patch history data for COL: {e}")

    return hist_df

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