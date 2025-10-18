import streamlit as st
import pandas as pd
from numpy.random import default_rng as rng
from folium.plugins import HeatMap

st.set_page_config(
    page_title="EMS Prediction Atlas",
    initial_sidebar_state="expanded",
    layout="wide"
)

# San Fran dummy-data map
sf_df = pd.DataFrame(
    rng(0).standard_normal((1000, 2)) / [50, 50] + [37.76, -122.4],
    columns=["lat", "lon"],
)
# New York dummy-data map
ny_df = pd.DataFrame(
    rng(0).standard_normal((1000, 2)) / [50, 50] + [40.7128, -74.0060],
    columns=["lat", "lon"],
)

# Title
st.markdown("<h1 style='text-align: left;'>EMS Prediction Atlas</h1>", unsafe_allow_html=True)
# Description
st.write("Welcome to the EMS Prediction Atlas — an open-source, real-time heat map platform that visualizes the volume and distribution of emergency service calls across geographic regions.\n " \
"By aggregating and categorizing data by incident type, time, and location, this platform delivers actionable insights for emergency services, policymakers, and researchers.\n" \
"Through open data analytics, geospatial visualization, and predictive modeling, the Atlas promotes community resilience, operational efficiency, and data-driven decision-making across public and private sectors.")


selected_city = st.sidebar.selectbox("Select City", ["San Francisco", "New York"])
notes, maps = st.columns([1,3], gap="small")
# Map selection
if selected_city == "San Francisco":
    with maps:
        st.markdown("<h1 style='text-align: center;'>Heat Map</h1>", unsafe_allow_html=True)
        st.map(sf_df)  

    with notes:
        st.markdown("<h1 style='text-align: center;'>Information</h1>", unsafe_allow_html=True)
        st.write("Ipsum Lorem")

elif selected_city == "New York":
    with maps:
        st.markdown("<h1 style='text-align: center;'>Heat Map</h1>", unsafe_allow_html=True)
        st.map(ny_df)  

    with notes:
        st.markdown("<h1 style='text-align: center;'>Information</h1>", unsafe_allow_html=True)
        st.write("Ipsum Lorem")