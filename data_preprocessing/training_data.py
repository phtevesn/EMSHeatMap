import pandas as pd
from pathlib import Path

from emt_data import get_emt_data
from weather_data import get_weather_data
from match_weather_data import match_weather_data
from add_non_emergency import add_non_emergency
from grid import find_cells

levels = 4
RAW_EMT_DATA_PATH = '../data/ready_emt_data.parquet'


def get_training_data():
    if Path(RAW_EMT_DATA_PATH).exists():
        emt_data = pd.read_parquet(RAW_EMT_DATA_PATH)
    else:
        emt_data = get_emt_data()

    emt_data = find_cells(emt_data, levels)
    emt_data = add_non_emergency(emt_data)
    weather_data = get_weather_data()
    combined_df = match_weather_data(emt_data=emt_data, weather_data=weather_data)

    return combined_df