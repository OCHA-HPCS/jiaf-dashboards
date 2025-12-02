import pandas as pd
import streamlit as st
import yaml
import os

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
def load_raw_data(iso):
    config = get_config(iso)
    file_path = config['file_path']
    sheet_names = [
        config['sheets']['pin'],
        config['sheets']['history'],
        config['sheets']['severity']
    ]
    return pd.read_excel(file_path, sheet_name=sheet_names, header=None, engine="calamine")

@st.cache_data(ttl=3600)
def load_df(iso):
    # Load config and data
    config = get_config(iso)
    raw_data = load_raw_data(iso)
    sheet_name = config['sheets']['pin']
    df = raw_data[sheet_name].copy()
    
    header_row = config['params'].get('header_row', 2)
    start_row = config['params'].get('start_row', 3)
    
    df.columns = df.iloc[header_row]
    df = df.iloc[start_row:].reset_index(drop=True)
    
    # Handle mapping: Internal -> Excel
    # We want to rename Excel columns to Internal names
    mapping = config.get('column_mapping', {})
    inv_map = {v: k for k, v in mapping.items()}
    df = df.rename(columns=inv_map)
    
    sectors = config.get('sectors', [])
    
    # Convert numeric columns first
    numeric_cols = ["Final PiN", "Population"] + sectors
    for col in numeric_cols:
        if col in df.columns:
             df[col] = pd.to_numeric(df[col], errors='coerce')

    # Check for Population Group aggregation
    # We assume Admin 2 P-Code is the unique identifier for the area
    pcode_col = config.get('geo', {}).get('pcode_col', "Admin 2 P-Code")
    
    if "Population Group" in df.columns and pcode_col in df.columns:
        # Columns to group by (preserve Admin 1 and Admin 2 names)
        group_cols = [pcode_col]
        if "Admin 1" in df.columns:
            group_cols.append("Admin 1")
        if "Admin 2" in df.columns:
            group_cols.append("Admin 2")
            
        # Columns to sum (PiN, Population, Sector PiNs)
        agg_dict = {}
        for col in numeric_cols:
            if col in df.columns:
                agg_dict[col] = "sum"
        
        # Perform aggregation
        df = df.groupby(group_cols, as_index=False).agg(agg_dict)

    df["Final PiN"] = pd.to_numeric(df["Final PiN"], errors='coerce', downcast="integer")
    # Ensure Population is numeric if we are going to divide by it
    if "Population" in df.columns:
        df["% PiN"] = df["Final PiN"] / df["Population"]
    
    # Calculate sector percentages after aggregation if needed? 
    # The original code calculated % PiN but didn't seem to use sector % explicitly from source except for one specific vis.
    # But for consistency, if we summed PiNs, we can re-calculate derived metrics if necessary.
    # The current app mostly uses raw PiN numbers or calculates percentages on the fly.
    
    return df

@st.cache_data(ttl=3600)
def load_hist(iso):
    config = get_config(iso)
    raw_data = load_raw_data(iso)
    sheet_name = config['sheets']['history']
    hist_df = raw_data[sheet_name].copy()
    
    header_row = config['params'].get('header_row', 2)
    start_row = config['params'].get('start_row', 3)
    
    hist_df.columns = hist_df.iloc[header_row]
    hist_df = hist_df.iloc[start_row:].reset_index(drop=True)
    
    # Mapping
    mapping = config.get('column_mapping', {})
    inv_map = {v: k for k, v in mapping.items()}
    hist_df = hist_df.rename(columns=inv_map)
    
    sectors = config.get('sectors', [])
    sectors_old = [f"{sector} - old" for sector in sectors]
    sectors_new = [f"{sector} - new" for sector in sectors]
    
    # Convert to numeric
    numeric_cols = []
    for old, new in zip(sectors_old, sectors_new):
        if old in hist_df.columns:
            hist_df[old] = pd.to_numeric(hist_df[old], errors='coerce')
            numeric_cols.append(old)
        if new in hist_df.columns:
            hist_df[new] = pd.to_numeric(hist_df[new], errors='coerce')
            numeric_cols.append(new)
            
    # Aggregation if Population Group exists
    pcode_col = config.get('geo', {}).get('pcode_col', "Admin 2 P-Code")
    if "Population Group" in hist_df.columns and pcode_col in hist_df.columns:
        group_cols = [pcode_col]
        if "Admin 1" in hist_df.columns:
            group_cols.append("Admin 1")
        if "Admin 2" in hist_df.columns:
            group_cols.append("Admin 2")
            
        agg_dict = {col: "sum" for col in numeric_cols}
        hist_df = hist_df.groupby(group_cols, as_index=False).agg(agg_dict)

    # Calculate deltas if columns exist
    # We sum assuming columns exist; if not, it might error or sum to 0.
    # Safer to filter existing columns
    existing_new = [c for c in sectors_new if c in hist_df.columns]
    existing_old = [c for c in sectors_old if c in hist_df.columns]
    
    if existing_new and existing_old:
        hist_df["PiN Delta"] = hist_df[existing_new].sum(axis=1) - hist_df[existing_old].sum(axis=1)
        hist_df["PiN Delta %"] = hist_df["PiN Delta"] / hist_df[existing_old].sum(axis=1).replace({0: pd.NA})
        hist_df["Old PiN"] = hist_df[existing_old].sum(axis=1)
        hist_df["New PiN"] = hist_df[existing_new].sum(axis=1)
        
    return hist_df

@st.cache_data(ttl=3600)
def load_sev(iso):
    config = get_config(iso)
    raw_data = load_raw_data(iso)
    sheet_name = config['sheets']['severity']
    sev_df = raw_data[sheet_name].copy()
    
    header_row = config['params'].get('header_row', 2)
    start_row = config['params'].get('start_row', 3)
    
    sev_df.columns = sev_df.iloc[header_row]
    sev_df = sev_df.iloc[start_row:].reset_index(drop=True)
    
    # Mapping
    # Note: Severity sheet might have different column names than PiN sheet?
    # If so, we might need separate mappings or be more flexible.
    # For now, we try to apply the mapping.
    mapping = config.get('column_mapping', {})
    inv_map = {v: k for k, v in mapping.items()}
    sev_df = sev_df.rename(columns=inv_map)

    sectors = config.get('sectors', [])
    for s in sectors:
        if s in sev_df.columns:
            sev_df[s] = pd.to_numeric(sev_df[s], errors='coerce')
            
    # Handle potential duplicates if any (though likely unique per area)
    # If there are multiple rows per area (which there shouldn't be for severity), take the first or max?
    # Prompt says "severity data isn't disaggregated", so we assume 1 row per area.
    # However, to be safe against duplicates which might break choropleths:
    pcode_col = config.get('geo', {}).get('pcode_col', "Admin 2 P-Code")
    if pcode_col in sev_df.columns:
         sev_df = sev_df.drop_duplicates(subset=[pcode_col])
         
    return sev_df