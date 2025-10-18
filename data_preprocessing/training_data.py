import pandas as pd
from pathlib import Path

from weather_data import get_weather_data
from match_weather_data import match_weather_data
from add_non_emergency import add_non_emergency
from grid import find_cells, grid_to_coords

levels = 4
RAW_EMT_DATA_PATH = '../data/2000_2006_subset_raw_emt_data.parquet'


def get_training_data():
    if Path(RAW_EMT_DATA_PATH).exists():
        emt_data = pd.read_parquet(RAW_EMT_DATA_PATH)
    else:
        raise FileNotFoundError(f"Raw EMT data not found at {RAW_EMT_DATA_PATH}")

    emt_data = emt_data.dropna(subset=['latitude', 'longitude'])

    emt_data, lats, lons = find_cells(emt_data, levels)
    emt_data = add_non_emergency(emt_data)

    emt_data["latitude"] = emt_data.apply(
        lambda r: grid_to_coords(r["cell"], lats, lons)[0],
        axis=1
    )
    emt_data["longitude"] = emt_data.apply(
        lambda r: grid_to_coords(r["cell"], lats, lons)[1],
        axis=1
    )

    weather_data = get_weather_data()
    combined_df = match_weather_data(emt_data=emt_data, weather_data=weather_data)

    final_df = combined_df[
        ['cell', 'year', 'month', 'day', 'hour', 'fmax', 'fmin', 'prcp_in', 'snow_in', 'emergency_count']].copy()

    final_df['snow_in'] = final_df['snow_in'].fillna("0.0")

    final_df = final_df.dropna()

    dtype_map = {
        'cell': 'int64',
        'year': 'int64',
        'month': 'int64',
        'day': 'int64',
        'hour': 'int64',
        'fmax': 'float64',
        'fmin': 'float64',
        'prcp_in': 'float64',
        'snow_in': 'float64',
        'emergency_count': 'int64'
    }

    # Apply conversions safely
    for col, dtype in dtype_map.items():
        if col in final_df.columns:
            final_df[col] = pd.to_numeric(final_df[col], errors='coerce').astype(dtype)

    return final_df
