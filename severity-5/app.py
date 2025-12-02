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
# Store the raw form data (non-indexed) for order-based lookup
form_df_raw = fetch_form(survey_id)
# Keep the indexed version for standard question lookups (used in charts and view dialog)
form_df = form_df_raw.drop_duplicates(subset="$xpath").set_index("$xpath")


# --- HELPER FUNCTION: GET LABELS BY FORM ORDER ---
def get_justification_labels_by_order(form_df_raw, prefix_path):
    """Infers labels for justification fields by checking the preceding element in form order."""

    form_elements = form_df_raw.reset_index(drop=True)

    # FIX APPLIED HERE: Use na=False to ensure the mask is purely boolean
    form_elements = form_elements[form_elements['$xpath'].str.startswith(prefix_path + '/', na=False)].reset_index(
        drop=True)

    justif_labels = {}

    for i, row in form_elements.iterrows():
        xpath = row['$xpath']

        is_justif_field = ('justif' in xpath.lower() or 'justify' in xpath.lower()) and row['type'] == 'text'

        if is_justif_field:
            current_label = row['label']

            if not pd.isna(current_label) and current_label.strip() != "":
                justif_labels[xpath] = current_label

            elif i > 0:
                prev_row = form_elements.loc[i - 1]
                inferred_label = prev_row['label']

                if not pd.isna(inferred_label) and inferred_label.strip() != "":
                    justif_labels[xpath] = f"{inferred_label} (Justification)"
                else:
                    clean_name = xpath.split('/')[-1]
                    lower_clean_name = clean_name.lower()
                    unwanted_prefixes = [
                        'please_justify_your_s_about_', 'justification_for_',
                        'please_justify_', 'justify_', 'please_', 'justif_'
                    ]
                    for prefix in unwanted_prefixes:
                        if lower_clean_name.startswith(prefix):
                            clean_name = clean_name[len(prefix):]
                            lower_clean_name = clean_name.lower()

                    final_label = clean_name.replace('_', ' ').strip()
                    justif_labels[xpath] = f"⚠️ (Label Missing) {final_label if final_label else 'Unidentified Field'}"

            else:
                justif_labels[xpath] = f"⚠️ (Label Missing) {xpath.split('/')[-1].replace('_', ' ')}"

    return justif_labels


@st.dialog("View submission", width="large")
def view(row: pd.Series):
    st.markdown("""
    <style>
    .answer-badge {
        padding: 4px 8px;
        border-radius: 6px;
        color: white;
        font-weight: 600;
    }
    .answer-yes { background-color: #2ecc71; }
    .answer-no { background-color: #e74c3c; }
    .answer-rmi { background-color: #f39c12; }
    .answer-default { background-color: #7f8c8d; }
    .section-header {
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 1.3rem;
        margin-bottom: 0.5rem;
        color: #333;
    }
    .question-label {
        font-weight: 600;
        display: block;
        padding-top: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    sections = {
        "module1": [],
        "module2": [],
        "module3": [],
        "areas": []
    }

    for key, value in row.items():
        if key.startswith("_") or key.startswith("meta/"):
            continue
        if key not in form_df.index:
            continue
        label = form_df.at[key, "label"]
        if pd.isna(label) or label.strip() == "":
            continue
        prefix = key.split("/")[0]
        if prefix not in sections:
            continue

        v = str(value).lower().strip()
        if v == "yes":
            css_class = "answer-yes"
        elif v == "no":
            css_class = "answer-no"
        elif v == "rmi":
            css_class = "answer-rmi"
        else:
            css_class = "answer-default"

        sections[prefix].append((label, value, css_class))

    section_titles = {
        "module1": "Module 1",
        "module2": "Module 2",
        "module3": "Module 3",
        "areas": "Areas"
    }

    for section_key in ["module1", "module2", "module3", "areas"]:
        items = sections[section_key]
        if not items:
            continue
        st.markdown(f"<div class='section-header'>{section_titles[section_key]}</div>",
                    unsafe_allow_html=True)
        for label, value, css_class in items:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(
                    f"<span class='question-label'>{label}</span>",
                    unsafe_allow_html=True
                )
            with col2:
                st.markdown(
                    f"<span class='answer-badge {css_class}'>{value}</span>",
                    unsafe_allow_html=True
                )


for i, module in enumerate(st.tabs(["Module 1", "Module 2", "Module 3", "Areas", "Submissions"])):
    if i < 3:
        with module:
            st.markdown(f"## Module {i + 1}")
            module_prefix = f"module{i + 1}"
            module_cols = df.columns[df.columns.str.startswith(module_prefix)]

            # --- Calculation and Charting ---
            df_justif = df[module_cols[df[module_cols].columns.str.contains("justif")]]
            df_justif.columns = df_justif.columns.str[-2:]
            df_module = df[module_cols].apply(pd.Series.value_counts).fillna(0).T
            df_module = df_module[[col for col in ["yes", "no", "rmi"] if col in df_module.columns]]
            df_module = df_module[(df_module.T != 0).any()]
            df_module["label"] = df_module.index.map(
                lambda x: form_df.at[x, "label"] if x in form_df.index else x
            )
            # FIX applied to the index mask
            oo_df = df_module[~df_module.index.str.contains("Workspace", na=False)]
            df_module.drop(oo_df.index, inplace=True)
            st.markdown(f"#### Outcome Indicator")
            x_arr = ["yes", "no", "rmi"]
            available_cols = [c for c in x_arr if c in oo_df.columns]
            if available_cols:
                oo_long = (
                    oo_df.reset_index()[["label"] + available_cols]
                    .melt(
                        id_vars="label",
                        value_vars=available_cols,
                        var_name="Response",
                        value_name="Count"
                    )
                )
                fig = px.bar(
                    oo_long,
                    y="label",
                    x="Count",
                    color="Response",
                    orientation="h",
                    color_discrete_map={
                        "yes": "green",
                        "no": "red",
                        "rmi": "orange"
                    },
                    labels={"label": "Question", "Count": "Count", "Response": "Response"}
                )
                fig.update_layout(
                    xaxis={"tickvals": list(range(0, int(oo_long["Count"].max()) + 1))},
                    margin=dict(t=0, l=0, r=0, b=0),
                    height=140,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No valid response columns (yes/no/rmi) found for this module.")
            st.markdown(f"#### Questions")
            x_arr = ["yes", "no", "rmi"]
            available_cols = [c for c in x_arr if c in df_module.columns]
            if available_cols:
                df_module_long = (
                    df_module.reset_index()[["label"] + available_cols]
                    .melt(
                        id_vars="label",
                        value_vars=available_cols,
                        var_name="Response",
                        value_name="Count"
                    )
                )
                fig = px.bar(
                    df_module_long,
                    y="label",
                    x="Count",
                    color="Response",
                    orientation="h",
                    color_discrete_map={
                        "yes": "green",
                        "no": "red",
                        "rmi": "orange"
                    },
                    labels={"label": "Question", "Count": "Count", "Response": "Response"}
                )
                fig.update_layout(
                    xaxis={
                        "tickvals": list(
                            range(0, int(df_module_long["Count"].max()) + 1)
                        )
                    },
                    margin=dict(t=0, l=0, r=0, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No valid response columns (yes/no/rmi) found for this module.")

            # --------------------------------------------------------------------------
            # --- Justification Display Start (Order-Based Logic) ----------------------
            # --------------------------------------------------------------------------
            st.markdown("#### Justifications")

            module_prefix_path = f"module{i + 1}"

            # Use the new function to map justification columns to their inferred labels
            justif_labels = get_justification_labels_by_order(form_df_raw, module_prefix_path)

            justif_cols_in_df = [col for col in df.columns if col in justif_labels]

            if not justif_cols_in_df:
                st.info("No justification fields found for this module.")
            else:
                for justif_col in justif_cols_in_df:
                    question_label = justif_labels[justif_col]

                    # Extract non-missing justification comments
                    comments_series = df[justif_col].astype(str).str.strip()

                    comments_filtered = comments_series[
                        (~comments_series.isin(['nan', 'NaN', ''])) &
                        (comments_series.notna())
                        ]

                    comments = comments_filtered.tolist()

                    if comments:
                        st.markdown(f"##### 📝 {question_label}")
                        # Display comments as a list
                        st.markdown(
                            "\n".join([f"* **Submission Comment:** {comment}" for comment in comments])
                        )
                        st.markdown("---")  # Separator between questions
            # --- Justification Display End ---
            # --------------------------------------------------------------------------

    elif i == 3:
        with module:
            st.markdown("## Areas Reviewed")
            area_cols = [col for col in df.columns if col.startswith("areas") and not "Justif" in col]
            df_areas = df[area_cols].apply(pd.Series.value_counts).fillna(0).T
            df_areas = df_areas[[col for col in ["yes", "no", "rmi"] if col in df_areas.columns]]
            df_areas = df_areas[(df_areas.T != 0).any()]
            df_areas["label"] = df_areas.index.map(
                lambda x: form_df.at[x, "label"] if x in form_df.index else x
            )
            x_arr = ["yes", "no", "rmi"]
            available_cols = [c for c in x_arr if c in df_areas.columns]
            if available_cols:
                df_areas_long = (
                    df_areas.reset_index()[["label"] + available_cols]
                    .melt(
                        id_vars="label",
                        value_vars=available_cols,
                        var_name="Response",
                        value_name="Count"
                    )
                )
                fig = px.bar(
                    df_areas_long,
                    y="label",
                    x="Count",
                    color="Response",
                    orientation="h",
                    color_discrete_map={
                        "yes": "green",
                        "no": "red",
                        "rmi": "orange"
                    },
                    labels={"label": "Area", "Count": "Count", "Response": "Response"}
                )
                fig.update_layout(
                    xaxis={"tickvals": list(range(0, int(df_areas_long["Count"].max()) + 1))},
                    margin=dict(t=0, l=0, r=0, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No valid response columns (yes/no/rmi) found for Areas.")

            # --------------------------------------------------------------------------
            # --- Areas Justification Display Start (Order-Based Logic) ----------------
            # --------------------------------------------------------------------------
            st.markdown("#### Areas Justifications")

            area_prefix_path = "areas"

            # Use the new function to map justification columns to their inferred labels
            justif_labels = get_justification_labels_by_order(form_df_raw, area_prefix_path)

            justif_cols_in_df = [col for col in df.columns if col in justif_labels]

            if not justif_cols_in_df:
                st.info("No justification fields found for Areas.")
            else:
                for justif_col in justif_cols_in_df:
                    area_label = justif_labels[justif_col]

                    # Extract non-missing justification comments
                    comments_series = df[justif_col].astype(str).str.strip()

                    comments_filtered = comments_series[
                        (~comments_series.isin(['nan', 'NaN', ''])) &
                        (comments_series.notna())
                        ]

                    comments = comments_filtered.tolist()

                    if comments:
                        st.markdown(f"##### 📝 {area_label}")
                        st.markdown(f"###### Field: `{justif_col}`")
                        # Display comments as a list
                        st.markdown(
                            "\n".join([f"* **Submission Comment:** {comment}" for comment in comments])
                        )
                        st.markdown("---")  # Separator between areas
            # --- Areas Justification Display End ---
            # --------------------------------------------------------------------------

    else:
        with module:
            st.markdown("## All Submissions")
            for idx, row in df.iterrows():
                if st.button(row["Name"]):
                    view(row)
