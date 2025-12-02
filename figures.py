import json
from urllib.request import urlopen, Request

import geopandas as gpd
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from pandas import DataFrame
from data import get_config

MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoiY3lydXMtcGVsbGV0IiwiYSI6ImNtaGttcjE2dzFpNzEyanNoejA2d2UycnMifQ.8pSHcMqcZiNnzY8w2mAg9A"

SEV_DM = {
    "1": "#f7fbff",
    "2": "#deebf7",
    "3": "#9ecae1",
    "4": "#3182bd",
    "5": "#08519c"
}


@st.cache_data(ttl=86400)
def load_cods(uri):
    req = Request(uri, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req) as response:
        return json.load(response)


@st.cache_data(ttl=86400)
def get_cods_gdf(uri):
    cods = load_cods(uri)
    return gpd.GeoDataFrame.from_features(cods["features"])


def auto_center_zoom(codes, iso):
    config = get_config(iso)
    uri = config['cod_uri']
    key = config.get('geo', {}).get('geojson_key', 'properties.#adm2+code+v_pcode')
    prop_name = key.replace("properties.", "")
    
    gdf = get_cods_gdf(uri)
    # Ensure the property exists in GDF
    if prop_name not in gdf.columns:
        # Fallback or error?
        # If property is inside "properties", from_features handles it. 
        # Sometimes naming might differ slightly?
        pass

    if prop_name in gdf.columns:
        subset = gdf[gdf[prop_name].isin(codes)]
    else:
        subset = pd.DataFrame() # Empty

    if subset.empty:
        # Default center if no match
        return {"lon": 35, "lat": -18}, 5

    minx, miny, maxx, maxy = subset.total_bounds
    center = {"lon": (minx + maxx) / 2, "lat": (miny + maxy) / 2}
    lon_range = maxx - minx
    zoom = 6.5 - np.log(lon_range + 1e-6)  # tweak constant as needed
    zoom = float(np.clip(zoom, 3, 8))  # clamp between sensible bounds
    return center, zoom


@st.cache_data(ttl=3600)
def _make_choropleth_internal(
        df: DataFrame,
        iso: str,
        color_col: str,
        legend: str,
        color_scale: str,
        discrete_map: dict,
        all_categories: list,
        continuous: bool
):
    config = get_config(iso)
    uri = config['cod_uri']
    pcode_col = config.get('geo', {}).get('pcode_col', "Admin 2 P-Code")
    geojson_key = config.get('geo', {}).get('geojson_key', "properties.#adm2+code+v_pcode")
    
    cods = load_cods(uri)
    
    center, zoom = auto_center_zoom(df[pcode_col], iso)

    if not continuous and all_categories:
        missing_categories = set(all_categories) - set(df[color_col].unique())
        if missing_categories:
            dummy_df = DataFrame({
                pcode_col: ["DUMMY"] * len(missing_categories),
                color_col: list(map(str, missing_categories)),
                "Admin 2": [""] * len(missing_categories)
            })
            df = pd.concat([df, dummy_df], ignore_index=True)

    if not continuous and all_categories:
        df = df[df[color_col].isin(map(str, all_categories))]

    fig = px.choropleth_mapbox(
        df,
        geojson=cods,
        color=color_col,
        locations=pcode_col,
        featureidkey=geojson_key,
        hover_name="Admin 2" if "Admin 2" in df.columns else None,
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
            marker_opacity=[0 if x == "DUMMY" else 1 for x in df[pcode_col]]
        )

    fig.update_layout(
        mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar_title_text=legend)

    return fig

def make_choropleth(
        df: DataFrame,
        iso: str,
        color_col: str,
        legend: str,
        color_scale: str = "Greens",
        discrete_map: dict = None,
        all_categories: list = None,
        continuous: bool = False
):
    if discrete_map is None:
        discrete_map = {}
        
    # Optimization: Extract only necessary columns to speed up hashing
    config = get_config(iso)
    pcode_col = config.get('geo', {}).get('pcode_col', "Admin 2 P-Code")
    
    cols_to_keep = [pcode_col, color_col]
    if "Admin 2" in df.columns:
        cols_to_keep.append("Admin 2")
        
    # Drop duplicates if any (though likely unique per pcode usually)
    # We copy to avoid modifying original df
    mini_df = df[cols_to_keep].copy()
    
    return _make_choropleth_internal(
        mini_df, iso, color_col, legend, color_scale, discrete_map, all_categories, continuous
    )