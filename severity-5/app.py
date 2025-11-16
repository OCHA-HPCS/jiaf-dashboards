import pandas as pd
import plotly.express as px
import requests
import streamlit as st

surveys = {
    "Columbia": "ajiqJ68LUrt4d4v4yRb7gw",
    "Myanmar": "awizpCCNrU6UiXxcqf4grg"
}

st.set_page_config(layout="wide", page_title="JIAF Severity 5 Review Dashboard", page_icon="🌍")

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

st.title("JIAF Severity 5 Review Dashboard")
country = st.selectbox("Select Country", options=list(surveys.keys()))
survey_id = surveys[country]

API_KEY = "0b93ccf6941932f0b1e5cf5bdd9ad69a8fa87cef"


@st.cache_data(ttl=3600)
def fetch_data(survey_id: str) -> pd.DataFrame:
    headers = {"Authorization": f"Token {API_KEY}"}
    response = requests.get(f"https://kobo.unocha.org/assets/{survey_id}/submissions/?format=json", headers=headers)
    response.raise_for_status()
    data = response.json()
    return pd.json_normalize(data)


@st.cache_data(ttl=3600)
def fetch_form(survey_id: str) -> pd.DataFrame:
    headers = {"Authorization": f"Token {API_KEY}"}
    response = requests.get(f"https://kobo.unocha.org/api/v2/assets/{survey_id}/content/", headers=headers)
    response.raise_for_status()
    data = response.json()
    return pd.json_normalize(data["data"]["survey"])


df = fetch_data(survey_id)
form_df = fetch_form(survey_id)
form_df.set_index("$xpath", inplace=True)

for i, module in enumerate(st.tabs(["Module 1", "Module 2", "Module 3"])):
    with module:
        st.markdown(f"## Module {i + 1}")
        module_cols = df.columns[df.columns.str.startswith(f"module{i + 1}")]
        df_justif = df[module_cols[df[module_cols].columns.str.contains("justif")]]
        df_justif.columns = df_justif.columns.str[-2:]
        df_module = df[module_cols].apply(pd.Series.value_counts).fillna(0).T
        df_module = df_module[[col for col in ["yes", "no", "rmi"] if col in df_module.columns]]
        df_module = df_module[(df_module.T != 0).any()]
        df_module["label"] = df_module.index.map(
            lambda x: form_df.at[x, "label"] if x in form_df.index else x
        )
        # get the row whose index doesn't include Workspace into a new df
        oo_df = df_module[~df_module.index.str.contains("Workspace")]
        df_module.drop(oo_df.index, inplace=True)
        st.markdown(f"#### Outcome Indicator")
        fig = px.bar(oo_df, y="label", x=["yes", "no", "rmi"], orientation="h", color_discrete_map={
            "yes": "green",
            "no": "red",
            "rmi": "orange"}, labels={"label": "Question", "value": "Count", "variable": "Response"})
        fig.update_layout(xaxis={
            "tickvals": list(range(0, int(oo_df[["yes", "no", "rmi"]].sum().max()) + 1))},
            margin=dict(t=0, l=0, r=0, b=0), height=140)
        st.plotly_chart(fig, width="stretch")
        st.markdown(f"#### Questions")
        fig = px.bar(df_module, y="label", x=["yes", "no", "rmi"], orientation="h", color_discrete_map={
            "yes": "green",
            "no": "red",
            "rmi": "orange"}, labels={"label": "Question", "value": "Count", "variable": "Response"})
        fig.update_layout(xaxis={
            "tickvals": list(range(0, int(df_module[["yes", "no", "rmi"]].sum().max()) + 1))},
            margin=dict(t=0, l=0, r=0, b=0))
        st.plotly_chart(fig, width="stretch")
        st.markdown("#### Justifications")
        st.dataframe(df_justif)
