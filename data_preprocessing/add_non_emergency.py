# In add_non_emergency.py

import pandas as pd
import numpy as np


def add_non_emergency(emergency_df: pd.DataFrame):
    # Ensure date column is just date, not datetime for daily weather matching
    emergency_df['date_day'] = pd.to_datetime(emergency_df['date']).dt.date
    emergency_df['hour'] = pd.to_datetime(emergency_df['date']).dt.hour

    # Mark existing rows as emergencies
    emergency_df['is_emergency'] = 1

    # 1. Create the full scaffold of all possible date-hours and cells
    start_date = emergency_df['date'].min()
    end_date = emergency_df['date'].max()
    all_hours = pd.date_range(start=start_date, end=end_date, freq='H')
    all_cells = range(256)  # Assuming a 16x16 grid from levels=4

    scaffold_df = pd.DataFrame(
        [(hour, cell) for hour in all_hours for cell in all_cells],
        columns=['date', 'cell']
    )

    # 2. Left merge the scaffold with your actual emergency data
    # We aggregate emergencies in case multiple happen in the same cell in the same hour
    emergency_agg = emergency_df.groupby(['date', 'cell']).size().reset_index(name='emergency_count')

    merged_df = pd.merge(scaffold_df, emergency_agg, on=['date', 'cell'], how='left')

    # 3. Fill NaNs to create the 'is_emergency' target variable
    merged_df['is_emergency'] = np.where(merged_df['emergency_count'].notna(), 1, 0)
    merged_df = merged_df.drop(columns=['emergency_count'])

    # 4. Merge back weather data for the non-emergency rows
    # This requires having a daily weather dataframe ready
    daily_weather = emergency_df[['date_day', 'cell', 'fmax', 'fmin', 'prcp_in']].drop_duplicates()
    final_df = pd.merge(merged_df, daily_weather, on=['date_day', 'cell'], how='left')

    # Forward-fill weather data for hours where no emergencies happened anywhere
    final_df = final_df.sort_values(['cell', 'date']).ffill()

    return final_df