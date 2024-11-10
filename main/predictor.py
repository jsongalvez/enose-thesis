# coding: future_fstrings

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
import joblib
import datetime
import csv
from pathlib import Path


class SensorPredictor:
    def __init__(self, model_path="model.joblib", scaler_path="scaler.joblib"):
        """
        Initialize the predictor with pre-trained model and scaler.

        Args:
            model_path: Path to saved RandomForest model
            scaler_path: Path to saved StandardScaler
        """
        # Load the pre-trained model and scaler
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

        # Define the expected features and their order
        self.numerical_features = [
            "MQ2",
            "MQ3",
            "MQ4",
            "MQ5",
            "MQ6",
            "MQ8",
            "MQ135",
            "PWR",
            "Temperature",
            "Humidity",
        ]

        # Create results.csv if it doesn't exist
        self.results_file = Path("results.csv")
        if not self.results_file.exists():
            with open(self.results_file, "w", newline="") as f:
                writer = csv.writer(f)
                headers = (
                    ["Timestamp"]
                    + self.numerical_features
                    # + ["MQ2_MQ3_ratio", "Prediction"]
                )
                writer.writerow(headers)

    def process_sensor_data(self, sensor_data):
        """
        Process raw sensor data and prepare it for prediction.

        Args:
            sensor_data: dict with keys matching numerical_features

        Returns:
            processed_data: DataFrame with scaled features
        """
        # Create DataFrame from sensor data
        df = pd.DataFrame([sensor_data])

        # Ensure all required features are present
        for feature in self.numerical_features:
            if feature not in df.columns:
                # raise ValueError(f"Missing required feature: {feature}")
                raise ValueError("Missing required feature: " + str(feature))

        # Scale the numerical features
        df.loc[:, self.numerical_features] = self.scaler.transform(
            df[self.numerical_features]
        )

        # Add engineered features
        # df["MQ2_MQ3_ratio"] = df["MQ2"] / df["MQ3"]

        return df

    def predict_and_log(self, sensor_data):
        """
        Process sensor data, make prediction, and log results.

        Args:
            sensor_data: dict with sensor readings

        Returns:
            prediction: int (0 or 1)
            probability: float (prediction probability)
        """
        try:
            # Add timestamp to sensor data
            current_time = datetime.datetime.now().isoformat(timespec="milliseconds")

            # Process the data
            processed_data = self.process_sensor_data(sensor_data)

            # Make prediction
            prediction = self.model.predict(processed_data[self.numerical_features])[0]
            probability = self.model.predict_proba(
                processed_data[self.numerical_features]
            )[0][1]

            # Prepare row for logging
            log_data = {
                "Timestamp": current_time,
                **sensor_data,
                # "MQ2_MQ3_ratio": processed_data["MQ2_MQ3_ratio"].iloc[0],
                "Prediction": prediction,
            }

            # Append to CSV
            with open(self.results_file, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=log_data.keys())
                writer.writerow(log_data)

            return prediction, probability

        except Exception as e:
            print("Error in prediction pipeline: " + str(e))
            return None, None


# Example usage:
if __name__ == "__main__":
    # First, save your trained model and scaler
    """
    joblib.dump(final_model, 'model.joblib')
    joblib.dump(scaler, 'scaler.joblib')
    """

    # Initialize the predictor
    predictor = SensorPredictor()

    # Example sensor data
    sensor_data = {  # Bagoong, Barrio Fiesta
        "MQ2": 529.875,
        "MQ3": 627.5625,
        "MQ4": 505.875,
        "MQ5": 32.4375,
        "MQ6": 347.8125,
        "MQ8": 143.8125,
        "MQ135": 916.3125,
        "PWR": 5014.6875,
        "Temperature": 57.6,
        "Humidity": 25.3,
    }
    # Make prediction
    prediction, probability = predictor.predict_and_log(sensor_data)
    print("Prediction: " + str(prediction))
    print("Probability: " + str(probability))
