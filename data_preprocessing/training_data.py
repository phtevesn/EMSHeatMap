import pandas as pd
from pathlib import Path

from weather_data import get_weather_data
from match_weather_data import match_weather_data
from add_non_emergency import add_non_emergency
from grid import find_cells, grid_to_coords_vectorized

levels = 4
RAW_EMT_DATA_PATH = '../data/2000_2006_subset_raw_emt_data.parquet'
grid_columns = 50
grid_rows = 50
total_cells = grid_columns * grid_rows


def get_training_data():
    if Path(RAW_EMT_DATA_PATH).exists():
        emt_data = pd.read_parquet(RAW_EMT_DATA_PATH)
    else:
        raise FileNotFoundError(f"Raw EMT data not found at {RAW_EMT_DATA_PATH}")
    print("Raw EMT data loaded successfully.")

    emt_data = emt_data.dropna(subset=['latitude', 'longitude'])

    emt_data, lats, lons = find_cells(emt_data, grid_columns, grid_rows)
    print("Grid successfully.")

    emt_data = add_non_emergency(emt_data, total_cells)
    print("Non-emergency data added successfully.")

    lat_series, lon_series = grid_to_coords_vectorized(emt_data['cell'], lats, lons)

    # Assign the new columns in one go
    emt_data['latitude'] = lat_series
    emt_data['longitude'] = lon_series
    print("Coordinates added successfully.")

    weather_data = get_weather_data()
    print("Weather data loaded successfully.")

    combined_df = match_weather_data(emt_data=emt_data, weather_data=weather_data)
    print("Weather data matched successfully.")

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
