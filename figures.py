import json
from urllib.request import urlopen

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from pandas import DataFrame

MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoiY3lydXMtcGVsbGV0IiwiYSI6ImNtaGttcjE2dzFpNzEyanNoejA2d2UycnMifQ.8pSHcMqcZiNnzY8w2mAg9A"
COD_URI = "https://itos-humanitarian.s3.amazonaws.com/MOZ/COD_MOZ_Admin2.geojson"

SEV_DM = {
    "1": "#f7fbff",
    "2": "#deebf7",
    "3": "#9ecae1",
    "4": "#3182bd",
    "5": "#08519c"
}


@st.cache_data(ttl=86400)
def load_cods():
    with urlopen(COD_URI) as response:
        return json.load(response)


cods = load_cods()


def auto_center_zoom(geojson, codes):
    gdf = gpd.GeoDataFrame.from_features(geojson["features"])
    subset = gdf[gdf["#adm2+code+v_pcode"].isin(codes)]
    minx, miny, maxx, maxy = subset.total_bounds
    center = {"lon": (minx + maxx) / 2, "lat": (miny + maxy) / 2}
    lon_range = maxx - minx
    zoom = 6.5 - np.log(lon_range + 1e-6)  # tweak constant as needed
    zoom = float(np.clip(zoom, 3, 8))  # clamp between sensible bounds
    return center, zoom


def make_choropleth(
        df: DataFrame,
        color_col: str,
        legend: str,
        color_scale: str = "Greens",
        discrete_map: dict = {},
        all_categories: list = None,
        continuous: bool = False
):
    center, zoom = auto_center_zoom(cods, df["Admin 2 P-Code"])

    if not continuous and all_categories:
        missing_categories = set(all_categories) - set(df[color_col].unique())
        if missing_categories:
            dummy_df = DataFrame({
                "Admin 2 P-Code": ["DUMMY"] * len(missing_categories),
                color_col: list(map(str, missing_categories)),
                "Admin 2": [""] * len(missing_categories)
            })
            df = pd.concat([df, dummy_df], ignore_index=True)

    # filter values not in all_categories
    if not continuous and all_categories:
        df = df[df[color_col].isin(map(str, all_categories))]

    fig = px.choropleth_mapbox(
        df,
        geojson=cods,
        color=color_col,
        locations="Admin 2 P-Code",
        featureidkey="properties.#adm2+code+v_pcode",
        hover_name="Admin 2",
        mapbox_style="light",
        center=center,
        zoom=zoom,
        color_continuous_scale=color_scale if continuous else None,
        color_discrete_map=discrete_map if not continuous else None,
        category_orders={
            color_col: all_categories if all_categories else []
        } if not continuous else None,
    )

    if not continuous and all_categories and missing_categories:
        fig.update_traces(
            selector=dict(type="choroplethmapbox"),
            marker_opacity=[0 if x == "DUMMY" else 1 for x in df["Admin 2 P-Code"]]
        )

    fig.update_layout(
        mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar_title_text=legend)

    return fig
