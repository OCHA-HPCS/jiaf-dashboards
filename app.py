import streamlit as st
import glob
import yaml
import os

st.set_page_config(layout="wide", page_title="JIAF Dashboard", page_icon="🌍")

# Reducing whitespace on the top of the page
st.markdown("""
<style>
.block-container
{
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}

[data-testid="stSidebarNav"]::before {
    content: "JIAF Dashboard";
    font-size: 20px;
}
</style>
""", unsafe_allow_html=True)

def get_iso_from_params():
    return st.query_params.get("iso", None)

def load_country_config(iso):
    try:
        iso = iso.upper()
        path = f"config/{iso}.yaml"
        if os.path.exists(path):
            with open(path, "r") as f:
                return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    return None

def landing_page():
    st.title("Select a Country")
    configs = glob.glob("config/*.yaml")
    countries = []
    for c in configs:
        iso = os.path.splitext(os.path.basename(c))[0]
        with open(c, 'r') as f:
            try:
                data = yaml.safe_load(f)
                name = data.get('name', iso)
                countries.append((iso, name))
            except:
                pass
    
    if not countries:
        st.warning("No configurations found in config/")
        
    for iso, name in countries:
        # Using markdown link to reload with query param
        st.markdown(f"### [{name}](?iso={iso})")

# Session State Logic to persist ISO across navigation
if "iso" not in st.session_state:
    st.session_state.iso = None

iso_param = get_iso_from_params()

if iso_param:
    st.session_state.iso = iso_param
elif st.session_state.iso:
    # Restore param if missing but in session (e.g. sidebar navigation)
    st.query_params["iso"] = st.session_state.iso

iso = st.session_state.iso
config = None
if iso:
    config = load_country_config(iso)

if not config:
    pg = st.navigation([st.Page(landing_page, title="Home")])
    pg.run()
else:
    st.title(f"{config.get('name', iso)} - Humanitarian Needs 2026")
    
    pages = {
        "Overview": [
            st.Page("pages/intro.py", title="Introduction"),
            st.Page("pages/final_pin.py", title="Final PiN & Severity"),
        ],
        "PiN": [
            st.Page("pages/pin_1.py", title="PiN (1)"),
            st.Page("pages/pin_2.py", title="PiN (2)"),
            st.Page("pages/pin_3_1.py", title="PiN (3.1)"),
            st.Page("pages/pin_3_2.py", title="PiN (3.2)"),
            st.Page("pages/pin_4.py", title="PiN (4)"),
        ],
        "Severity": [
            st.Page("pages/sev_1.py", title="Severity (1)"),
            st.Page("pages/sev_2.py", title="Severity (2)"),
            st.Page("pages/sev_3_1.py", title="Severity (3.1)"),
            st.Page("pages/sev_3_2.py", title="Severity (3.2)"),
        ],
        "Linkages": [
            st.Page("pages/link_1.py", title="Links (1)"),
            st.Page("pages/link_2.py", title="Links (2)"),
        ],
    }
    
    pg = st.navigation(pages, position="sidebar")
    pg.run()