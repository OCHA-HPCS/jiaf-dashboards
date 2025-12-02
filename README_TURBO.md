# Turbo Mode for JIAF Dashboard

This dashboard includes a "Turbo Mode" that uses precomputed datasets to significantly speed up load times, especially for large Excel files.

## How to use

### 1. Install Dependencies
Ensure you have the required dependencies installed (especially `pyarrow` for Parquet support):
```bash
pip install -r requirements.txt
```

### 2. Precompute Data
Run the precomputation script. This script reads the Excel files defined in `config/*.yaml`, processes the data, and saves optimized Parquet files to the `precomputed/` directory.

```bash
python precompute.py
```

**Note:** You must re-run this script whenever the underlying Excel files or the configuration (mappings, etc.) change.

### 3. Run the App
You can run the standard app or the Turbo variant. Both will automatically use the precomputed data if it exists in the `precomputed/` folder.

```bash
streamlit run app_turbo.py
```

or

```bash
streamlit run app.py
```

If the precomputed files are missing, the app will fall back to processing the Excel files on the fly (slower).

## Structure
- `precompute.py`: Script to generate parquet files.
- `etl.py`: Core logic for data processing (separated from Streamlit).
- `app_turbo.py`: A variant of the entry point with a distinct title.
- `precomputed/`: Directory where optimized data files are stored.
