import pandas as pd
import numpy as np


def add_non_emergency(emergency_df: pd.DataFrame):
    """
    Expands the emergency call dataframe to include non-emergency time slots
    and retains the count of emergencies per hour as the target variable.

    Args:
        emergency_df: DataFrame containing only emergency events, with 'cell'
                      and weather data already assigned.

    Returns:
        A DataFrame with both emergency (count > 0) and non-emergency (count = 0) rows.
    """
    # --- 1. Prepare Timestamps and Identify Weather Columns ---

    emergency_df['date_hour'] = pd.to_datetime(emergency_df['date']).dt.floor('H')
    emergency_df['date_day'] = emergency_df['date_hour'].dt.date

    known_cols = ['call_number', 'incident_number', 'date', 'year', 'month', 'day',
                  'hour', 'longitude', 'latitude', 'cell', 'date_hour', 'date_day',
                  'emergency_count']
    weather_cols = [col for col in emergency_df.columns if col not in known_cols]

    # --- 2. Create the Full Scaffold (all hours, all cells) ---

    all_cells = emergency_df['cell'].unique()
    min_hour = emergency_df['date_hour'].min()
    max_hour = emergency_df['date_hour'].max()
    all_hours = pd.date_range(start=min_hour, end=max_hour, freq='H')

    scaffold_df = pd.DataFrame(
        index=pd.MultiIndex.from_product(
            [all_hours, all_cells], names=['date_hour', 'cell']
        )
    ).reset_index()

    # --- 3. Aggregate Emergency Counts and Merge onto Scaffold ---

    # This correctly counts multiple emergencies in the same hour/cell
    emergency_counts = emergency_df.groupby(['date_hour', 'cell']).size().reset_index(name='emergency_count')

    merged_df = pd.merge(
        scaffold_df,
        emergency_counts,
        on=['date_hour', 'cell'],
        how='left'
    )

    # Fill non-emergency slots with a count of 0. This is now our target variable.
    merged_df['emergency_count'] = merged_df['emergency_count'].fillna(0).astype(int)

    # --- 4. Add Weather Data to Non-Emergency Rows ---

    weather_to_merge = emergency_df[['date_hour', 'cell'] + weather_cols].drop_duplicates(subset=['date_hour', 'cell'])

    final_df = pd.merge(
        merged_df,
        weather_to_merge,
        on=['date_hour', 'cell'],
        how='left'
    )

    final_df['date_day'] = final_df['date_hour'].dt.date

    final_df = final_df.sort_values(by=['cell', 'date_hour'])
    final_df[weather_cols] = final_df.groupby(['cell', 'date_day'])[weather_cols].ffill().bfill()
    final_df = final_df.dropna(subset=weather_cols)

    final_df['year'] = final_df['date_hour'].dt.year
    final_df['month'] = final_df['date_hour'].dt.month
    final_df['day'] = final_df['date_hour'].dt.day
    final_df['hour'] = final_df['date_hour'].dt.hour
    final_df['date'] = pd.to_datetime(final_df[['year', 'month', 'day']])

    # Clean up helper columns, but KEEP emergency_count
    final_df = final_df.drop(columns=['date_day'])

    return final_df