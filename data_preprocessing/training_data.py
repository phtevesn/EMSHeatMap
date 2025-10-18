from emt_data import get_emt_data
from weather_data import get_weather_data
from match_weather_data import match_weather_data
from add_non_emergency import add_non_emergency
from grid import find_cells

levels = 4

def get_training_data():
    emt_data = get_emt_data()
    emt_data = find_cells(emt_data, levels)
    emt_data = add_non_emergency(emt_data)
    weather_data = get_weather_data()
    combined_df = match_weather_data(emt_data=emt_data, weather_data=weather_data)

    return combined_df