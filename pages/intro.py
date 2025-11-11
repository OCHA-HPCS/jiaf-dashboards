import streamlit as st

st.subheader("Needs Patterns and Sectoral Linkages Dashboard")
st.text(
    "Welcome to the Needs Patterns and Sectoral Linkages Dashboard, intended to support your analysis of the linkages, overlaps and trends of sectoral and intersectoral needs in step 3.6 of the JIAF (workspace 3C).")

st.subheader("Navigating the dashboard")
st.text(
    "The dashboard consists of 11 pages, organized around a set of questions to help guide discussions within sectors and in the multi-partner workshop. The graphs on each page allow you to filter geographic units, population groups, PiN values and PiN as % of population[KH1] , as well as severity levels, if relevant to the context of the page.")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown(
            ":green-background[**PiN (1)**: Where is the highest concentration of population in need in the country?]")
        st.markdown(
            "_This page gives an overview of how many people are in need in different parts of the country. The filters allow to switch between the distribution of PiN by administrative unit in absolute values and percentage of the total population of the unit considered._")
        st.page_link("pages/pin_1.py", label="Go to PiN (1)", icon="➡️")
    with st.container(border=True):
        st.markdown(
            ":green-background[**PiN (2)**: Which areas have a large number of sectors with a large PiN?]")
        st.markdown(
            "_This page presents which areas have a high concentration of sectors that have a PiN above a certain percentage of the population to support your analysis of high need concentration. It uses colors to represent the concentration of sectors with more people in need than the set threshold. The threshold can be set according to the context. The ‘% PiN’ filter also allows for easy identification of locations where PiN exceeds the total population, where data should be further scrutinized._")
        st.page_link("pages/pin_2.py", label="Go to PiN (2)", icon="➡️")
    with st.container(border=True):
        st.markdown(
            ":green-background[**PiN (3)**: Which sectors have the highest PiN?]")
        st.markdown(
            "_**(Q3.1)** This page maps PiN distribution by sector to support your analysis of PiN trends and drivers. Hovering over the maps displays the overall PiN and an overview of sectoral PiN for the selected area. It’s also possible to use the admin unit filters to focus on specific locations._")
        st.page_link("pages/pin_3_1.py", label="Go to PiN (3.1)", icon="➡️")
        st.markdown(
            "_**(Q3.2)** The graphs on this page show which sectors have the highest PiN per area (use the admin unit filters to focus on specific locations), how many people are in need for each sector (use the filter to show individual population groups where available), and in how many areas each sector has the highest or second highest PiN._")
        st.page_link("pages/pin_3_2.py", label="Go to PiN (3.2)", icon="➡️")
    with st.container(border=True):
        st.markdown(
            ":green-background[**PiN (4)**:  What is the PiN Trend as compared to the previous year?]")
        st.markdown(
            "_The final page presents the change in Pin figures from the previous year, geographically and in my sector, to support your analysis of trends in PiN over time. Use the filter to focus on changes in specific locations or shifts in individual population groups._")
        st.page_link("pages/pin_4.py", label="Go to PiN (4)", icon="➡️")
with col2:
    with st.container(border=True):
        st.markdown(
            ":blue-background[**Severity (1)**:  Where are the areas with the highest severity?]")
        st.markdown(
            "_This page maps intersectoral severity and lists severity levels by administrative unit, supporting analysis of patterns, potential errors in severity classification, or trends in areas where severity levels stay consistently high._")
        st.page_link("pages/sev_1.py", label="Go to Severity (1)", icon="➡️")
    with st.container(border=True):
        st.markdown(
            ":blue-background[**Severity (2)**:  Which areas have a large number of sectors with high severity of needs?]")
        st.markdown(
            "_This analysis identifies areas with multiple sectors exceeding a predetermined severity threshold to support analysis of geographic patterns in sectoral severities. You can adjust the severity threshold to focus on areas of high severity convergence, and hover over the map to display sectoral severity for each location._")
        st.page_link("pages/sev_2.py", label="Go to Severity (2)", icon="➡️")
    with st.container(border=True):
        st.markdown(
            ":blue-background[**Severity (3)**: Which sectors have the highest severity? (i.e., which sectors are driving the needs in a given area?]")
        st.markdown(
            "_**(Q6.1)** This page maps severity by sector to support your analysis of severity patterns and drivers. Hovering over each map displays the overall severity per location as well as a breakdown of sectoral severity for that location (use the admin unit filters to focus on specific locations)._")
        st.page_link("pages/sev_3_1.py", label="Go to Severity (3.1)", icon="➡️")
        st.markdown(
            "_**(Q6.2)** The graphs on this page show the number of locations under each severity level by sector (use the filters to show specific locations and severity levels), and a list of high-severity sectors per area._")
        st.page_link("pages/sev_3_2.py", label="Go to Severity (3.2)", icon="➡️")
    with st.container(border=True):
        st.markdown(
            ":violet-background[**Linkages (1)**: Pin-Severity Coexistence Analysis: Identifying High-Need Sectors]")
        st.markdown(
            "_This page maps the convergence of overall PiN and intersectoral severity levels to support your analysis of highest need areas. This analysis focuses on identifying sectors with both high severity levels (severity 4 and 5) and high PiN within a given area. Suggestion is to adjust the filters to focus on high severity levels (use severity 4 and 5) and areas where PiN constituted a high % of the total population._")
        st.page_link("pages/link_1.py", label="Go to Link (1)", icon="➡️")
    with st.container(border=True):
        st.markdown(
            ":violet-background[**Linkages (2)**: To what extent do sectoral PiNs correlate?]")
        st.markdown(
            "_This analysis examines the correlation between sectoral PiNs (use the administrative unit filters to look at correlations in specific locations). A coefficient close to 1 suggests a strong correlation, while a coefficient closer to 0 suggests no correlation between sectoral PiN figures. When there is an expectation of a close relationship between sectors, but the data doesn't confirm it, it may indicate issues with assumptions or data quality._")
        st.page_link("pages/link_2.py", label="Go to Link (2)", icon="➡️")
