import pandas as pd
import faiss


def match_weather_data(weather_data: pd.DataFrame = None, emt_data: pd.DataFrame = None):
    weather_required_columns = ['year', 'month', 'day', 'latitude', 'longitude']
    emt_required_columns = ['year', 'month', 'day', 'latitude', 'longitude']

    # Check weather_data
    missing_weather_cols = [col for col in weather_required_columns if col not in weather_data.columns]
    if missing_weather_cols:
        raise ValueError(f"weather_data is missing columns: {missing_weather_cols}")

    # Check emt_data
    missing_emt_cols = [col for col in emt_required_columns if col not in emt_data.columns]
    if missing_emt_cols:
        raise ValueError(f"emt_data is missing columns: {missing_emt_cols}")

    # Unique weather station coords
    weather_coords = weather_data[['latitude', 'longitude']].drop_duplicates().to_numpy().astype('float64')

    # Build the FAISS index
    index = faiss.IndexFlatL2(weather_coords.shape[1])  # L2 = Euclidean
    index.add(weather_coords)

    # Query for nearest station for each call
    call_coords = emt_data[['latitude', 'longitude']].to_numpy().astype('float32')
    distances, indices = index.search(call_coords, 1)  # k=1 nearest

    # Map the nearest station coords back
    nearest_weather_coords = weather_coords[indices.flatten()]
    emt_data['nearest_lat'] = nearest_weather_coords[:, 0]
    emt_data['nearest_lon'] = nearest_weather_coords[:, 1]

    merged = pd.merge(
        emt_data,
        weather_data,
        left_on=['nearest_lat', 'nearest_lon', 'date'],
        right_on=['latitude', 'longitude', 'date'],
        how='inner'
    )

    merged = merged.drop(
        columns=['latitude_y', 'longitude_y', 'nearest_lat', 'nearest_lon', 'date', 'year_y', 'month_y', 'day_y'])

    merged = merged.rename(columns={'year_x': 'year'})
    merged = merged.rename(columns={'day_x': 'day'})
    merged = merged.rename(columns={'month_x': 'month'})
    merged = merged.rename(columns={'longitude_x': 'longitude'})
    merged = merged.rename(columns={'latitude_x': 'latitude'})

    merged = merged.dropna(subset=["latitude", "longitude"])

    return merged


if __name__ == "__main__":
    weather_data = pd.read_csv('../data/weather.csv')
    emt_data = pd.read_parquet('../data/processed_ems_data.parquet')

    match_weather_data(weather_data, emt_data)