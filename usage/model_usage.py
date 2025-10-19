import pandas as pd
import joblib
from datetime import datetime
from typing import Optional


class EmergencyPredictor:
    """
    A class to load a trained XGBoost model and use it to predict
    the number of emergencies using historical weather data.
    """

    def __init__(self, model_path: str, weather_data_path: str):
        """
        Initializes the predictor by loading the model and historical weather data.

        Args:
            model_path (str): The file path to the saved .joblib model.
            weather_data_path (str): Path to the CSV file containing historical weather.
        """
        self.model = self._load_model(model_path)
        self.daily_weather = self._load_and_prepare_weather(weather_data_path)
        self.features_order = [
            'cell', 'year', 'month', 'day', 'hour',
            'fmax', 'fmin', 'prcp_in', 'snow_in'
        ]

    def _load_model(self, model_path: str):
        """Loads the saved XGBoost model from a file."""
        try:
            print(f"Loading model from {model_path}...")
            model = joblib.load(model_path)
            print("Model loaded successfully.")
            return model
        except FileNotFoundError:
            print(f"Error: Model file not found at '{model_path}'.")
            raise

    def _load_and_prepare_weather(self, weather_path: str) -> pd.DataFrame:
        """Loads and prepares weather data for quick lookups."""
        print(f"Loading and preparing weather data from {weather_path}...")
        weather_df = pd.read_csv(weather_path)
        weather_df['date'] = pd.to_datetime(weather_df['Date']).dt.date

        # We average the weather from all stations for each day
        # This provides a single set of weather values for any given day
        daily_avg_weather = weather_df.groupby('date').mean(numeric_only=True)
        print("Weather data is ready.")
        return daily_avg_weather

    def predict(self, target_datetime: datetime, num_cells: int = 256) -> pd.DataFrame:
        """
        Makes a prediction for a specific date and time across all grid cells
        using historical weather data.

        Args:
            target_datetime (datetime): The date and time to generate a prediction for.
            num_cells (int): The total number of grid cells in the map.

        Returns:
            pd.DataFrame: A DataFrame containing 'cell_id' and 'prediction' columns.
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded. Cannot make predictions.")

        print(f"\nGenerating predictions for {target_datetime.strftime('%Y-%m-%d %H:%M:%S')}...")

        # --- 1. Look up the historical weather for the target day ---
        target_date = target_datetime.date()
        try:
            weather_for_day = self.daily_weather.loc[target_date]
        except KeyError:
            print(f"Error: No historical weather data found for {target_date}.")
            raise

        # --- 2. Create the model input DataFrame ---
        df = pd.DataFrame({'cell': range(1, num_cells + 1)})
        df['year'] = target_datetime.year
        df['month'] = target_datetime.month
        df['day'] = target_datetime.day
        df['hour'] = target_datetime.hour

        # Use the actual historical weather data
        df['fmax'] = weather_for_day['fmax']
        df['fmin'] = weather_for_day['fmin']
        df['prcp_in'] = weather_for_day['prcp_in']
        df['snow_in'] = weather_for_day['snow_in']

        # --- 3. Predict and format results ---
        predictions = self.model.predict(df[self.features_order])
        predictions = predictions.clip(0)  # Ensure no negative predictions

        result_df = pd.DataFrame({
            'cell_id': df['cell'],
            'prediction': predictions
        })

        print("Prediction complete.")
        return result_df


# --- Example of How to Use the Class ---
if __name__ == '__main__':
    # DEFINE YOUR FILE PATHS HERE
    # NOTE: You may need to create a single 'weather.csv' from your two files first
    # Or adjust the path to point to one of them, e.g., downtown.
    MODEL_FILE = '../model/emergency_prediction_model.joblib'
    WEATHER_FILE = '../data/sanfranciscodowntown.csv'  # Using one file as an example

    try:
        # 1. Initialize the predictor with paths to your model and weather data
        predictor = EmergencyPredictor(model_path=MODEL_FILE, weather_data_path=WEATHER_FILE)

        # 2. Define a time in a year the model was NOT trained on (e.g., 2007)
        # Let's predict for a summer evening in 2007
        prediction_time = datetime(2007, 7, 15, 18, 0, 0)  # 6:00 PM on July 15, 2007

        # 3. Call the predict method
        prediction_results = predictor.predict(target_datetime=prediction_time, num_cells=256)

        # 4. Display the results
        print("\n--- Prediction Results ---")
        print(prediction_results.head())

        print("\n--- Top 5 Hottest Cells ---")
        print(prediction_results.sort_values('prediction', ascending=False).head())

    except Exception as e:
        print(f"An error occurred during the prediction process: {e}")