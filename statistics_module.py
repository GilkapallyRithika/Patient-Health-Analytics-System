"""
statistics_module.py
Provides descriptive statistics functions and a feature-level summary utility.
"""

import math
from collections import Counter


class StatisticsCalculator:
    """Computes common descriptive statistics from a list of numeric values."""

    def __init__(self, values: list):
        self.values = [v for v in values if v is not None]
        if not self.values:
            raise ValueError("No valid numeric values provided.")

    def mean(self) -> float:
        return sum(self.values) / len(self.values)

    def median(self) -> float:
        sorted_vals = sorted(self.values)
        n = len(sorted_vals)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
        return float(sorted_vals[mid])

    def mode(self):
        """Return the most frequent value (first encountered if tied)."""
        counts = Counter(self.values)
        return counts.most_common(1)[0][0]

    def minimum(self) -> float:
        return min(self.values)

    def maximum(self) -> float:
        return max(self.values)

    def data_range(self) -> float:
        return self.maximum() - self.minimum()

    def variance(self) -> float:
        m = self.mean()
        return sum((x - m) ** 2 for x in self.values) / len(self.values)

    def std_dev(self) -> float:
        return math.sqrt(self.variance())

    def summary(self) -> dict:
        """Return all statistics as a single dictionary."""
        return {
            "count": len(self.values),
            "mean": round(self.mean(), 4),
            "median": round(self.median(), 4),
            "mode": self.mode(),
            "minimum": self.minimum(),
            "maximum": self.maximum(),
            "range": round(self.data_range(), 4),
            "variance": round(self.variance(), 4),
            "std_dev": round(self.std_dev(), 4),
        }


class FeatureStatistics:
    """Extracts a numeric feature from patient_data and computes its statistics."""

    def __init__(self, patient_data: list[dict]):
        self.patient_data = patient_data

    def describe(self, feature_name: str) -> dict:
        """Return descriptive stats dict for the given feature column."""
        values = self._extract_values(feature_name)
        calc = StatisticsCalculator(values)
        result = {"feature": feature_name}
        result.update(calc.summary())
        return result

    def _extract_values(self, feature_name: str) -> list:
        values = []
        for patient in self.patient_data:
            val = patient.get(feature_name)
            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    pass
        if not values:
            raise ValueError(f"Feature '{feature_name}' not found or has no numeric data.")
        return values
