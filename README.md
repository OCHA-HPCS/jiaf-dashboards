# JIAF Dashboard

The **JIAF (Joint Intersectoral Analysis Framework) Dashboard** is a Streamlit-based application designed to visualize and analyze humanitarian needs data. It provides interactive visualizations for Population in Need (PiN), Severity of needs, and sectoral linkages, facilitating the Step 3.6 analysis in the JIAF process.

## Features

- **Multi-Country Support**: Dynamically loads configurations and datasets for different countries based on YAML configuration files.
- **Interactive Visualizations**:
  - **PiN Analysis**: Geographic distribution, sector concentration, and historical trends.
  - **Severity Analysis**: Intersectoral severity mapping and sector-specific drivers.
  - **Linkages**: Correlation analysis between sectoral PiNs and severity/PiN overlaps.
- **Turbo Mode**: Optional pre-computation pipeline to convert heavy Excel sheets into optimized Parquet files for instant dashboard loading.
- **Configurable**: Highly flexible column mapping and sheet configuration via YAML.

## Installation

### Prerequisites
- Python 3.10 or higher
- Recommended: A virtual environment

### Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd jiaf-dashboards
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # macOS/Linux
   python -m venv .venv
   source .venv/bin/activate

   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the App
You can start the dashboard using Streamlit:

```bash
streamlit run app.py
```

Navigate to `http://localhost:8501` in your browser.

### Turbo Mode (Fast Loading)
For large datasets, parsing Excel files on every load can be slow. "Turbo Mode" uses precomputed Parquet files.

1. **Precompute the data:**
   Runs the ETL process on configured Excel files and saves optimized artifacts to `precomputed/`.
   ```bash
   python precompute.py
   ```

2. **Run the Turbo App:**
   ```bash
   streamlit run app_turbo.py
   ```
   *(Note: The standard `app.py` will also automatically use precomputed files if they exist.)*

## Configuration

To add a new country or update an existing one:

1. **Add Data**: Place the Excel file (e.g., `MOZ_Worksheet...xlsx`) in the project root or a data directory.
2. **Create Config**: Create a YAML file in the `config/` directory (e.g., `MOZ.yaml`).

### Config Structure (Example)

```yaml
name: "Mozambique"
file_path: "MOZ_Worksheet_3A_3B_PiN_Sev_V4_2026_1_original.xlsx"

sheets:
  pin: "WS - 3.1 Overall PiN"
  severity: "WS - 3.2 Intersectoral Severity"
  history: "PiN Historical Trend"

params:
  header_row: 2
  start_row: 3

geo:
  pcode_col: "Admin 2 P-Code"

sectors:
  - "Food Security"
  - "WASH"
  - "Health"
  # ...

column_mapping:
  "Admin 1": "Admin 1"
  "Admin 2": "Admin 2"
  "Admin 2 P-Code": "Admin 2 P-Code"
  "Population": "Total Population"
  "Final PiN": "Overall PiN"
  "Final Severity": "Intersectoral Severity"
  # Map internal names (keys) to Excel headers (values)
```

## Docker Deployment

The application is containerized for easy deployment.

1. **Build the image:**
   ```bash
   docker build -t jiaf-dashboard .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8501:8501 jiaf-dashboard
   ```

## Project Structure

- `app.py`: Main entry point for the standard application.
- `app_turbo.py`: Entry point for the Turbo variant.
- `pages/`: Contains the individual Streamlit pages (PiN, Severity, Linkages).
- `config/`: YAML configuration files for each country.
- `data.py`: Functions for loading data (uses caching).
- `etl.py`: Core data processing logic (extract/transform).
- `precompute.py`: Script to generate optimized Parquet files.
- `deploy/`: Kubernetes/Kustomize deployment manifests.
- `severity-5/`: Sub-application or specialized view for Severity 5 analysis.
