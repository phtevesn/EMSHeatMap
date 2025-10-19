import pandas as pd
import xgboost as xgb
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from datetime import datetime

# --- 1. Load and Prepare Data ---

# Load your final dataset
# This assumes the data is in the same directory. Update the path if needed.
try:
    df = pd.read_parquet('../data/2000_2006_32x32_training.parquet')
except FileNotFoundError:
    print("Error: Data file not found. Please update the path to your dataset.")
    # Create a dummy dataframe based on your example to allow the script to run
    df = pd.DataFrame({
        'cell': [0, 1, 2, 3, 4],
        'year': [2000] * 5,
        'month': [4] * 5,
        'day': [1] * 5,
        'hour': [20, 21, 22, 23, 24],
        'fmax': [73.0] * 5,
        'fmin': [52.0] * 5,
        'prcp_in': [0.26] * 5,
        'snow_in': [0.0] * 5,
        'emergency_count': [0, 1, 0, 0, 2]
    })

print("Data loaded successfully.")
print(f"Dataset shape: {df.shape}")

# Define features (X) and the target (y)
# We drop non-feature columns. 'date_hour' is used for splitting but not for training.
features = [
    'cell', 'year', 'month', 'day', 'hour',
    'fmax', 'fmin', 'prcp_in', 'snow_in'
]
target = 'emergency_count'

X = df[features]
y = df[target]


# --- 2. Time-Based Data Splitting ---

# CRITICAL: For time-series data, you must split by time, not randomly.
# We will use 2000-2005 for training and 2006 for testing.

train_df = df[df['year'] <= 2005]
test_df = df[df['year'] == 2006]

# Check if the test set is empty
if test_df.empty:
    raise ValueError("The test set is empty. Please ensure your data includes the year 2006.")

# Separate features and target for train and test sets
X_train = train_df[features]
y_train = train_df[target]
X_test = test_df[features]
y_test = test_df[target]

print(f"Training data shape: {X_train.shape}")
print(f"Testing data shape: {X_test.shape}")
print(f"Training on years: {sorted(train_df['year'].unique())}")
print(f"Testing on year: {sorted(test_df['year'].unique())}")


# --- 3. Train the XGBoost Regressor Model ---

print("\nTraining XGBoost model...")
start = datetime.now()

# Initialize the XGBoost Regressor
# These are good starting hyperparameters.
# n_estimators: Number of boosting rounds (trees).
# learning_rate: Step size shrinkage to prevent overfitting.
# max_depth: Maximum depth of a tree.
# subsample: Fraction of samples to be used for fitting each tree.
# colsample_bytree: Fraction of features to be used for fitting each tree.
# enable_categorical=True: Lets XGBoost handle the 'cell' column automatically.
xgb_reg = xgb.XGBRegressor(
    n_estimators=1000,
    learning_rate=0.05,
    max_depth=7,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    enable_categorical=True,  # Important for handling the 'cell' feature
    n_jobs=-1,  # Use all available CPU cores,
    early_stopping_rounds=50,  # Stop if MAE doesn't improve for 50 rounds
    eval_metric='mae' # Mean Absolute Error
)

# Train the model with early stopping
# Early stopping prevents overfitting by stopping training when the validation score stops improving.
xgb_reg.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=True
)

print(f"Total training time: {(datetime.now() - start).total_seconds():.2f} seconds")
print("\nModel training complete.")


# --- 4. Evaluate the Model ---

print("\nEvaluating model performance...")

# Make predictions on the test set
y_pred = xgb_reg.predict(X_test)

# Calculate evaluation metrics
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Absolute Error (MAE): {mae:.4f}")
print(f"Mean Squared Error (MSE): {mse:.4f}")
print(f"R-squared (R²): {r2:.4f}")

# Interpretation of metrics:
# MAE: On average, the model's prediction is off by ~{mae:.2f} emergencies.
# R²: The model explains ~{r2:.1%} of the variance in the emergency count.


# --- 5. Save the Trained Model ---

# Save the model to a file for later use (e.g., in your mapping script)
model_filename = '../model/emergency_prediction_model.joblib'
joblib.dump(xgb_reg, model_filename)

print(f"\nModel saved successfully to {model_filename}")