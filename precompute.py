import os
import glob
import pandas as pd
import etl

PRECOMPUTED_DIR = "precomputed"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def precompute_country(iso):
    print(f"Processing {iso}...")
    try:
        config = etl.load_config(iso)
    except Exception as e:
        print(f"  Skipping {iso}: {e}")
        return

    iso_dir = os.path.join(PRECOMPUTED_DIR, iso)
    ensure_dir(iso_dir)
    
    file_path = config.get('file_path')
    if not file_path or not os.path.exists(file_path):
        print(f"  File not found for {iso}: {file_path}")
        return

    # 1. Process PiN
    try:
        sheet_name = config['sheets']['pin']
        print(f"  Loading PiN sheet: {sheet_name}")
        raw_df = etl.load_raw_data_file(file_path, sheet_name)
        df_pin = etl.process_pin_data(config, raw_df)
        out_path = os.path.join(iso_dir, "pin.parquet")
        df_pin.to_parquet(out_path, index=False)
        print(f"  Saved {out_path}")
    except Exception as e:
        print(f"  Error processing PiN for {iso}: {e}")

    # 2. Process History
    try:
        sheet_name = config['sheets']['history']
        print(f"  Loading History sheet: {sheet_name}")
        raw_df = etl.load_raw_data_file(file_path, sheet_name)
        df_hist = etl.process_hist_data(config, raw_df)
        out_path = os.path.join(iso_dir, "hist.parquet")
        df_hist.to_parquet(out_path, index=False)
        print(f"  Saved {out_path}")
    except Exception as e:
        print(f"  Error processing History for {iso}: {e}")

    # 3. Process Severity
    try:
        sheet_name = config['sheets']['severity']
        print(f"  Loading Severity sheet: {sheet_name}")
        raw_df = etl.load_raw_data_file(file_path, sheet_name)
        df_sev = etl.process_sev_data(config, raw_df)
        out_path = os.path.join(iso_dir, "sev.parquet")
        df_sev.to_parquet(out_path, index=False)
        print(f"  Saved {out_path}")
    except Exception as e:
        print(f"  Error processing Severity for {iso}: {e}")

def main():
    ensure_dir(PRECOMPUTED_DIR)
    configs = glob.glob("config/*.yaml")
    
    if not configs:
        print("No configuration files found in config/")
        return

    for config_file in configs:
        iso = os.path.splitext(os.path.basename(config_file))[0]
        precompute_country(iso)
    
    print("Precomputation complete.")

if __name__ == "__main__":
    main()
