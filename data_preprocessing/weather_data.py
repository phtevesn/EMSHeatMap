import pandas as pd

"../data/sanfranciscodowntown.csv"
"../data/sanfranciscointernationalairport.csv"

DOWNTOWN_COORD = [37.7705, -122.4269]
AIRPORT_COORD = [37.61962, -122.36562]


def load_raw_weather_data(downtown_path: str, airport_path: str):
    downtown_df = pd.read_csv(downtown_path)
    airport_df = pd.read_csv(airport_path)

    # Set coordinates
    downtown_df["latitude"] = DOWNTOWN_COORD[0]
    downtown_df["longitude"] = DOWNTOWN_COORD[1]
    airport_df["latitude"] = AIRPORT_COORD[0]
    airport_df["longitude"] = AIRPORT_COORD[1]

    downtown_df =  downtown_df.drop("TAVG (Degrees Fahrenheit)", axis=1)
    airport_df = airport_df.drop("TAVG (Degrees Fahrenheit)", axis=1)

    weather_df = pd.concat([downtown_df, airport_df], ignore_index=True)

    weather_df = weather_df.rename(columns={
        'TMAX (Degrees Fahrenheit)': 'fmax',
        'TMIN (Degrees Fahrenheit)': 'fmin',
        'PRCP (Inches)': 'prcp_in',
        'SNOW (Inches)': 'snow_in',
        'SNWD (Inches)': 'snwd_in',
    })

    # Then reorder columns to the desired order:
    weather_df = weather_df[['Date', 'fmax', 'fmin', 'prcp_in', 'snow_in', 'snwd_in', 'latitude', 'longitude']]

    return weather_df


def format_date_columns(weather_df: pd.DataFrame):
    if 'Date' not in weather_df.columns:
        raise ValueError("df must contain a 'date' column")

    # Convert to datetime dtype
    weather_df['date'] = pd.to_datetime(weather_df['Date'])

    # Extract components
    weather_df['year'] = weather_df['date'].dt.year
    weather_df['month'] = weather_df['date'].dt.month
    weather_df['day'] = weather_df['date'].dt.day

    # Drop original columns (not needed anymore)
    weather_df = weather_df.drop(columns=['Date'])

    return weather_df


def get_weather_data():
    downtown_path = "../data/sanfranciscodowntown.csv"
    airport_path = "../data/sanfranciscointernationalairport.csv"

    weather_df = load_raw_weather_data(downtown_path, airport_path)
    weather_df = format_date_columns(weather_df)

    # select relevant columns
    weather_df = weather_df[
        ['year', 'month', 'date', 'day', 'fmax', 'fmin', 'prcp_in', 'snow_in', 'snwd_in', 'latitude', 'longitude']]

    return weather_df

