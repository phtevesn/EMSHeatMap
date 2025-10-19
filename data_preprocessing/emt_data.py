import os
from dotenv import load_dotenv

import pandas as pd
from sodapy import Socrata

load_dotenv()

def get_raw_emt_data(limit: int = 1000):
    # api endpoint
    url = "https://data.sfgov.org/api/v3/views/nuek-vuh3/query.csv"

    client = Socrata(
        "data.sfgov.org",
        os.getenv("SFGOV_APP_TOKEN"),
        username=os.getenv("SFGOV_EMAIL"),
        password=os.getenv("SFGOV_PASSWORD")
    )

    results = client.get("nuek-vuh3", limit=limit)

    # Convert to dataframe
    results_df = pd.DataFrame.from_records(results)

    return results_df


def format_date_columns(df: pd.DataFrame):
    if 'received_dttm' not in df.columns:
        raise ValueError("df must contain a 'received_dttm' column")

    # Convert to datetime dtype
    df['date'] = pd.to_datetime(df['received_dttm'])

    # Extract components
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['time'] = df['date'].dt.time
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

    # Drop original columns (not needed anymore)
    df = df.drop(columns=['received_dttm'])

    return df


def set_time_1_hour(df: pd.DataFrame):
    """
    We are putting the time interval to 1 hour. So we are just keeping the hour in the time column.
    """
    if 'time' not in df.columns:
        raise ValueError("df must contain a 'time' column")

    df['hour'] = df['time'].apply(lambda time: time.hour)

    # Drop time because we only need hour right now
    df = df.drop(columns=['time'])

    return df


def format_lat_lon_columns(df: pd.DataFrame):
    df['longitude'] = df['case_location'].apply(lambda x: x['coordinates'][0] if pd.notnull(x) else None)
    df['latitude'] = df['case_location'].apply(lambda x: x['coordinates'][1] if pd.notnull(x) else None)

    # Drop original columns (not needed anymore)
    df = df.drop(columns=['case_location'])

    return df


def get_emt_data(limit: int = 1000):
    """
    Get raw data, formats date columns, sets time to 1 hour, and formats lat/lon columns.
    """
    df = get_raw_emt_data(limit=limit)
    df = format_date_columns(df)
    df = set_time_1_hour(df)
    df = format_lat_lon_columns(df)

    df = df[
        ['call_number', 'incident_number', 'date', 'year', 'month', 'day', 'hour', 'longitude', 'latitude']]

    return df


if __name__ == "__main__":
    emt_data = get_emt_data(limit=8000000)
    emt_data.to_parquet('../data/ready_emt_data.parquet')




