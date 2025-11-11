import streamlit as st

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

</style>
""", unsafe_allow_html=True)

st.title("Mozambique - Humanitarian Needs 2026")

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
    "Correlations": [
        st.Page("pages/link_1.py", title="Links (1)"),
        st.Page("pages/link_2.py", title="Links (2)"),
    ],
}

pg = st.navigation(pages, position="sidebar")
pg.run()
