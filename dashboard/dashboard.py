import streamlit as st
import pandas as pd
from numpy.random import default_rng as rng

st.set_page_config(
    page_title="EMS Prediction Atlas",
    initial_sidebar_state="expanded",
    layout="wide"
)

df = pd.DataFrame(
    rng(0).standard_normal((1000, 2)) / [50, 50] + [37.76, -122.4],
    columns=["lat", "lon"],
)

notes, maps = st.columns([1,3], gap="small")
with maps:
    st.markdown("<h1 style='text-align: center;'>Heat Map</h1>", unsafe_allow_html=True)
    st.map(df)

with notes:
    st.markdown("<h1 style='text-align: center;'>Information</h1>", unsafe_allow_html=True)
    st.write("Ipsum Lorem")
