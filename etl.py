import pandas as pd
import yaml
import os

def load_config(iso):
    """Loads configuration for a given ISO without Streamlit dependencies."""
    if not iso:
        raise ValueError("No country selected.")
    iso = iso.upper()
    config_path = os.path.join("config", f"{iso}.yaml")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration for {iso} not found.")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_raw_data_file(file_path, sheet_name):
    """Loads raw data from Excel file."""
    return pd.read_excel(file_path, sheet_name=sheet_name, header=None, engine="calamine")

def clean_columns(df):
    """Cleans DataFrame columns: removes NaNs, ensures strings, removes duplicates."""
    # Remove columns where the name is NaN
    df = df.loc[:, df.columns.notna()]
    # Ensure all column names are strings
    df.columns = df.columns.astype(str)
    # Remove duplicate columns, keeping the first occurrence
    df = df.loc[:, ~df.columns.duplicated()]
    return df

def process_pin_data(config, df):
    """Processes the PiN data."""
    header_row = config['params'].get('header_row', 2)
    start_row = config['params'].get('start_row', 3)
    
    df.columns = df.iloc[header_row]
    df = clean_columns(df)
    df = df.iloc[start_row:].reset_index(drop=True)
    
    sectors = config.get('sectors', [])
    
    # Handle mapping: Internal -> Excel
    mapping = config.get('column_mapping', {})
    
    renames = {}
    aggregations = {}
    
    for k, v in mapping.items():
        if isinstance(v, str):
            renames[v] = k
        elif isinstance(v, list):
            # If it is a sector, aggregate. Else, treat as aliases (rename).
            if k in sectors:
                aggregations[k] = v
            else:
                for val in v:
                    renames[val] = k

    df = df.rename(columns=renames)

    # Apply aggregations
    for k, v in aggregations.items():
        # Sum columns if they exist
        cols_to_sum = [c for c in v if c in df.columns]
        if cols_to_sum:
            # Convert to numeric first to ensure summation works
            for c in cols_to_sum:
                df[c] = df[c].astype(str).replace({'-': '0'})
                df[c] = df[c].str.replace(r'NoPIN26\s*', '', regex=True)
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            
            df[k] = df[cols_to_sum].sum(axis=1)
    
    # Convert numeric columns
    numeric_cols = ["Final PiN", "Population"] + sectors
    for col in numeric_cols:
        if col in df.columns:
             # Replace excel-style hyphens with 0
             df[col] = df[col].astype(str).replace({'-': '0'})
             # Clean specific artifacts like "NoPIN26 "
             df[col] = df[col].str.replace(r'NoPIN26\s*', '', regex=True)
             df[col] = pd.to_numeric(df[col], errors='coerce')

    # Check for Population Group aggregation
    pcode_col = config.get('geo', {}).get('pcode_col', "Admin 2 P-Code")
    
    if pcode_col in df.columns:
        df = df.dropna(subset=[pcode_col])
    
    if "Population Group" in df.columns and pcode_col in df.columns:
        group_cols = [pcode_col]
        if "Admin 1" in df.columns:
            group_cols.append("Admin 1")
        if "Admin 2" in df.columns:
            group_cols.append("Admin 2")
            
        agg_dict = {}
        for col in numeric_cols:
            if col in df.columns:
                agg_dict[col] = "sum"
        
        df = df.groupby(group_cols, as_index=False).agg(agg_dict)

    df["Final PiN"] = pd.to_numeric(df["Final PiN"], errors='coerce', downcast="integer")
    if "Population" in df.columns:
        df["% PiN"] = df["Final PiN"] / df["Population"]
    
    # Ensure remaining object columns are strings to avoid Parquet inference issues
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str)

    return df

def process_hist_data(config, df):
    """Processes the historical data."""
    header_row = config['params'].get('header_row', 2)
    start_row = config['params'].get('start_row', 3)
    
    df.columns = df.iloc[header_row]
    df = clean_columns(df)
    df = df.iloc[start_row:].reset_index(drop=True)
    
    sectors = config.get('sectors', [])
    mapping = config.get('column_mapping', {})
    
    renames = {}
    aggregations = {}
    
    for k, v in mapping.items():
        if isinstance(v, str):
            renames[v] = k
        elif isinstance(v, list):
            # Check if k is related to a sector (exact match or history suffix)
            is_sector_related = k in sectors or \
                                (k.endswith(' - old') and k[:-6] in sectors) or \
                                (k.endswith(' - new') and k[:-6] in sectors)
            
            if is_sector_related:
                aggregations[k] = v
            else:
                for val in v:
                    renames[val] = k
    
    df = df.rename(columns=renames)
    
    for k, v in aggregations.items():
        # Sum columns if they exist
        cols_to_sum = [c for c in v if c in df.columns]
        if cols_to_sum:
            # Convert to numeric first
            for c in cols_to_sum:
                df[c] = df[c].astype(str).replace({'-': '0'})
                df[c] = df[c].str.replace(r'NoPIN26\s*', '', regex=True)
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            
            df[k] = df[cols_to_sum].sum(axis=1)
    sectors_old = [f"{sector} - old" for sector in sectors]
    sectors_new = [f"{sector} - new" for sector in sectors]
    
    numeric_cols = []
    for old, new in zip(sectors_old, sectors_new):
        if old in df.columns:
            df[old] = df[old].astype(str).replace({'-': '0'})
            df[old] = df[old].str.replace(r'NoPIN26\s*', '', regex=True)
            df[old] = pd.to_numeric(df[old], errors='coerce')
            numeric_cols.append(old)
        if new in df.columns:
            df[new] = df[new].astype(str).replace({'-': '0'})
            df[new] = df[new].str.replace(r'NoPIN26\s*', '', regex=True)
            df[new] = pd.to_numeric(df[new], errors='coerce')
            numeric_cols.append(new)
            
    pcode_col = config.get('geo', {}).get('pcode_col', "Admin 2 P-Code")
    
    if pcode_col in df.columns:
        df = df.dropna(subset=[pcode_col])
    
    if "Population Group" in df.columns and pcode_col in df.columns:
        group_cols = [pcode_col]
        if "Admin 1" in df.columns:
            group_cols.append("Admin 1")
        if "Admin 2" in df.columns:
            group_cols.append("Admin 2")
            
        agg_dict = {col: "sum" for col in numeric_cols}
        df = df.groupby(group_cols, as_index=False).agg(agg_dict)

    existing_new = [c for c in sectors_new if c in df.columns]
    existing_old = [c for c in sectors_old if c in df.columns]
    
    if existing_new and existing_old:
        df["PiN Delta"] = df[existing_new].sum(axis=1) - df[existing_old].sum(axis=1)
        df["PiN Delta %"] = df["PiN Delta"] / df[existing_old].sum(axis=1).replace({0: pd.NA})
        df["Old PiN"] = df[existing_old].sum(axis=1)
        df["New PiN"] = df[existing_new].sum(axis=1)
        
    # Ensure remaining object columns are strings to avoid Parquet inference issues
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str)

    return df

def process_sev_data(config, df):
    """Processes the severity data."""
    header_row = config['params'].get('header_row', 2)
    start_row = config['params'].get('start_row', 3)
    
    df.columns = df.iloc[header_row]
    df = clean_columns(df)
    df = df.iloc[start_row:].reset_index(drop=True)
    
    sectors = config.get('sectors', [])
    mapping = config.get('column_mapping', {})
    
    renames = {}
    aggregations = {}
    
    for k, v in mapping.items():
        if isinstance(v, str):
            renames[v] = k
        elif isinstance(v, list):
            if k in sectors:
                aggregations[k] = v
            else:
                for val in v:
                    renames[val] = k
    
    df = df.rename(columns=renames)
    
    for k, v in aggregations.items():
        # Sum columns if they exist
        cols_to_sum = [c for c in v if c in df.columns]
        if cols_to_sum:
            # Convert to numeric first
            for c in cols_to_sum:
                df[c] = df[c].astype(str).replace({'-': '0'})
                df[c] = df[c].str.replace(r'NoPIN26\s*', '', regex=True)
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            
            df[k] = df[cols_to_sum].sum(axis=1)
    for s in sectors:
        if s in df.columns:
            df[s] = df[s].astype(str).replace({'-': '0'})
            df[s] = df[s].str.replace(r'NoPIN26\s*', '', regex=True)
            df[s] = pd.to_numeric(df[s], errors='coerce')

    # Also clean and convert 'Final Severity' if present
    if "Final Severity" in df.columns:
         df["Final Severity"] = df["Final Severity"].astype(str).replace({'-': '0'})
         df["Final Severity"] = pd.to_numeric(df["Final Severity"], errors='coerce')
            
    pcode_col = config.get('geo', {}).get('pcode_col', "Admin 2 P-Code")
    if pcode_col in df.columns:
         df = df.drop_duplicates(subset=[pcode_col])
    
    # Ensure remaining object columns are strings to avoid Parquet inference issues
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str)
         
    return df
