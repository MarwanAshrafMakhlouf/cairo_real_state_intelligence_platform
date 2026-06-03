import streamlit as st 
import pandas as pd
from huggingface_hub import hf_hub_download
import yaml

@st.cache_data
def load_data():
    file_path = hf_hub_download(
        repo_id = st.secrets["HF_REPO"],
        filename = st.secrets["HF_FILENAME"],
        repo_type = st.secrets["HF_REPO_TYPE"],
        token = st.secrets["HF_TOKEN"]
    )
    return pd.read_parquet(file_path)

@st.cache_data
def location_loader():
    file_path = hf_hub_download(
        repo_id = st.secrets["HF_REPO"],
        filename = st.secrets["HF_LOCATIONS_FILENAME"],
        repo_type = st.secrets["HF_REPO_TYPE"],
        token = st.secrets["HF_TOKEN"]
    )
    with open(file_path, 'r') as f:
        location_data = yaml.safe_load(f)
    locations ={ }
    for district in location_data:
        d_name = district['district']
        locations[d_name] = {}
        for area in district.get("areas", []):
            a_name = area['name']
            locations[d_name][a_name] = [n["name"] for n in area.get("neighborhoods", [])]
    return locations