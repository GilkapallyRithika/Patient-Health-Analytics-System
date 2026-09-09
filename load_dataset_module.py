"""
load_dataset_module.py
Loads the patient health dataset from CSV into memory as a list of dictionaries.
"""

import csv
import os


class DatasetLoader:
    """Handles loading and type-conversion of the patient health CSV dataset."""

    # Columns that should be treated as integers
    INT_FIELDS = {
        "ID", "Hypertension", "Heart Disease", "Ever Married",
        "Alcohol Consumption", "Chronic Stress", "Sleep Hours",
        "Family History of Stroke", "Stroke Risk Score", "Stroke Occurrence"
    }

    # Columns that should be treated as floats
    FLOAT_FIELDS = {"Age", "Average Glucose Level", "BMI"}

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.patient_data: list[dict] = []

    def load(self) -> list[dict]:
        """Read CSV, convert types, and return list of patient dicts."""
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Dataset not found: {self.filepath}")

        with open(self.filepath, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                converted = self._convert_row(row)
                self.patient_data.append(converted)

        return self.patient_data

    def _convert_row(self, row: dict) -> dict:
        """Apply numeric type conversions to a single CSV row."""
        converted = {}
        for key, value in row.items():
            key = key.strip()
            value = value.strip()
            try:
                if key in self.INT_FIELDS:
                    converted[key] = int(value)
                elif key in self.FLOAT_FIELDS:
                    converted[key] = float(value)
                else:
                    converted[key] = value
            except ValueError:
                # Keep original string if conversion fails
                converted[key] = value
        return converted

    def get_data(self) -> list[dict]:
        return self.patient_data


def load_patient_data(filepath: str) -> list[dict]:
    """Convenience function: load dataset and return patient_data list."""
    loader = DatasetLoader(filepath)
    return loader.load()
