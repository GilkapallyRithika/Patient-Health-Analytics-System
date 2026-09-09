"""
query_module.py
Implements all 12 query functions for the patient health analytics system.
Results can be exported to CSV.
"""

import csv
import os
from statistics_module import StatisticsCalculator


class QueryEngine:
    """Runs all required queries against the loaded patient dataset."""

    def __init__(self, patient_data: list[dict]):
        self.data = patient_data

    # ------------------------------------------------------------------ helpers
    def _ages(self, subset: list[dict]) -> list:
        return [p["Age"] for p in subset if "Age" in p]

    def _stat_summary(self, values: list) -> dict:
        """Return mean/mode/median for a numeric list, or empty dict if no data."""
        if not values:
            return {"mean": None, "mode": None, "median": None}
        calc = StatisticsCalculator(values)
        return {
            "mean": round(calc.mean(), 4),
            "mode": calc.mode(),
            "median": round(calc.median(), 4),
        }

    def export_to_csv(self, results, filepath: str) -> None:
        """Persist query results (list of dicts) to a CSV file."""
        if not results:
            raise ValueError("No results to export.")
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        keys = results[0].keys() if isinstance(results[0], dict) else []
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            if keys:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(results)
            else:
                writer = csv.writer(f)
                for row in results:
                    writer.writerow([row])

    # ------------------------------------------------------------------ queries
    def query_1_smokers_with_hypertension_age_stats(self) -> dict:
        """
        Q1: Average, modal, and median age of patients who smoke/formerly smoked
        AND have hypertension.
        """
        subset = [
            p for p in self.data
            if p.get("Smoking Status") in ("Formerly smoked", "smokes")
            and p.get("Hypertension") == 1
        ]
        stats = self._stat_summary(self._ages(subset))
        return {"query": "Q1 - Smokers/Formerly smoked with Hypertension (Age stats)",
                "count": len(subset), **stats}

    def query_2_heart_disease_age_glucose(self) -> dict:
        """
        Q2: Average, modal, median age and average glucose level of patients
        with heart disease.
        """
        subset = [p for p in self.data if p.get("Heart Disease") == 1]
        age_stats = self._stat_summary(self._ages(subset))
        glucose_vals = [p["Average Glucose Level"] for p in subset if "Average Glucose Level" in p]
        avg_glucose = round(sum(glucose_vals) / len(glucose_vals), 4) if glucose_vals else None
        return {"query": "Q2 - Heart Disease Patients (Age & Glucose)",
                "count": len(subset),
                "age_mean": age_stats["mean"],
                "age_mode": age_stats["mode"],
                "age_median": age_stats["median"],
                "avg_glucose_level": avg_glucose}

    def query_3_gender_hypertension_stroke_age(self) -> list[dict]:
        """
        Q3: Average, modal, and median age grouped by gender, comparing
        hypertensive patients who had a stroke vs those who did not.
        """
        results = []
        for gender in ("Male", "Female"):
            for stroke in (1, 0):
                subset = [
                    p for p in self.data
                    if p.get("Gender") == gender
                    and p.get("Hypertension") == 1
                    and p.get("Stroke Occurrence") == stroke
                ]
                stats = self._stat_summary(self._ages(subset))
                results.append({
                    "gender": gender,
                    "stroke_occurrence": stroke,
                    "count": len(subset),
                    "age_mean": stats["mean"],
                    "age_mode": stats["mode"],
                    "age_median": stats["median"],
                })
        return results

    def query_4_physical_activity_bmi_glucose_stroke_risk(self) -> list[dict]:
        """
        Q4: Average BMI, glucose level, and stroke risk score for each
        physical activity level.
        """
        activity_levels = ("Sedentary", "Light", "Moderate", "Active")
        results = []
        for level in activity_levels:
            subset = [p for p in self.data if p.get("Physical Activity") == level]
            if not subset:
                continue

            def avg(field):
                vals = [p[field] for p in subset if field in p and p[field] is not None]
                return round(sum(vals) / len(vals), 4) if vals else None

            results.append({
                "physical_activity": level,
                "count": len(subset),
                "avg_bmi": avg("BMI"),
                "avg_glucose_level": avg("Average Glucose Level"),
                "avg_stroke_risk_score": avg("Stroke Risk Score"),
            })
        return results

    def query_5_residence_stroke_age_stats(self) -> list[dict]:
        """
        Q5: Average, modal, and median age of patients in Urban vs Rural areas
        who had a stroke.
        """
        results = []
        for residence in ("Urban", "Rural"):
            subset = [
                p for p in self.data
                if p.get("Residence Type") == residence
                and p.get("Stroke Occurrence") == 1
            ]
            stats = self._stat_summary(self._ages(subset))
            results.append({
                "residence_type": residence,
                "stroke_count": len(subset),
                "age_mean": stats["mean"],
                "age_mode": stats["mode"],
                "age_median": stats["median"],
            })
        return results

    def query_6_dietary_habits_stroke(self) -> list[dict]:
        """
        Q6: Dietary habits count for patients with stroke vs without stroke.
        """
        results = []
        for stroke in (1, 0):
            from collections import Counter
            subset = [p for p in self.data if p.get("Stroke Occurrence") == stroke]
            habits = Counter(p.get("Dietary Habits", "Unknown") for p in subset)
            for habit, count in habits.items():
                results.append({
                    "stroke_occurrence": stroke,
                    "dietary_habit": habit,
                    "count": count,
                })
        return results

    def query_7_hypertension_and_stroke(self) -> list[dict]:
        """
        Q7: All patients with Hypertension = 1 AND Stroke Occurrence = 1.
        """
        return [
            p for p in self.data
            if p.get("Hypertension") == 1 and p.get("Stroke Occurrence") == 1
        ]

    def query_8_heart_disease_and_stroke(self) -> list[dict]:
        """
        Q8: All patients with Heart Disease who experienced a stroke.
        """
        return [
            p for p in self.data
            if p.get("Heart Disease") == 1 and p.get("Stroke Occurrence") == 1
        ]

    def query_9_sleep_hours_by_stroke(self) -> list[dict]:
        """
        Q9: Average sleep hours for patients who had stroke vs those who did not.
        """
        results = []
        for stroke in (1, 0):
            subset = [p for p in self.data if p.get("Stroke Occurrence") == stroke]
            hours = [p["Sleep Hours"] for p in subset if "Sleep Hours" in p and p["Sleep Hours"] is not None]
            avg = round(sum(hours) / len(hours), 4) if hours else None
            results.append({
                "stroke_occurrence": stroke,
                "count": len(subset),
                "avg_sleep_hours": avg,
            })
        return results

    def query_10_flexible_filter(
        self,
        age_min: float = None,
        age_max: float = None,
        gender: str = None,
        smoking_status: str = None,
        region: str = None,
    ) -> list[dict]:
        """
        Q10: Filter patients by any combination of age range, gender,
        smoking status, and region.
        """
        subset = self.data
        if age_min is not None:
            subset = [p for p in subset if p.get("Age", -1) >= age_min]
        if age_max is not None:
            subset = [p for p in subset if p.get("Age", 9999) <= age_max]
        if gender:
            subset = [p for p in subset if p.get("Gender", "").lower() == gender.lower()]
        if smoking_status:
            subset = [p for p in subset if p.get("Smoking Status", "").lower() == smoking_status.lower()]
        if region:
            subset = [p for p in subset if p.get("Region", "").lower() == region.lower()]
        return list(subset)

    def query_11_risk_group_categorisation(self) -> list[dict]:
        """
        Q11: Categorise patients into Low / Medium / High risk groups based on
        Stroke Risk Score, returning count and percentage for each group.
        """
        groups = {"Low": 0, "Medium": 0, "High": 0}
        total = len(self.data)
        for p in self.data:
            score = p.get("Stroke Risk Score", 0)
            if score < 34:
                groups["Low"] += 1
            elif score < 67:
                groups["Medium"] += 1
            else:
                groups["High"] += 1
        results = []
        for group, count in groups.items():
            results.append({
                "risk_group": group,
                "count": count,
                "percentage": round((count / total) * 100, 2) if total else 0,
            })
        return results

    def query_12_regional_health_summary(self) -> list[dict]:
        """
        Q12: Summary comparing average age, BMI, glucose level, and stroke
        occurrence rate across regions (North, South, East, West).
        """
        regions = ("North", "South", "East", "West")
        results = []
        for region in regions:
            subset = [p for p in self.data if p.get("Region") == region]
            if not subset:
                continue

            def avg(field):
                vals = [p[field] for p in subset if field in p and p[field] is not None]
                return round(sum(vals) / len(vals), 4) if vals else None

            stroke_count = sum(1 for p in subset if p.get("Stroke Occurrence") == 1)
            stroke_rate = round((stroke_count / len(subset)) * 100, 2) if subset else 0

            results.append({
                "region": region,
                "total_patients": len(subset),
                "avg_age": avg("Age"),
                "avg_bmi": avg("BMI"),
                "avg_glucose_level": avg("Average Glucose Level"),
                "stroke_count": stroke_count,
                "stroke_occurrence_rate_%": stroke_rate,
            })
        return results
