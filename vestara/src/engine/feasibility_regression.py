"""
Feasibility Regressor — GradientBoostingRegressor that predicts months_to_achieve_goal.
Post-processing classifies the residual into Green/Yellow/Red verdicts.

Refactor of the original FeasibilityClassifier (which achieved 99.9% accuracy
by memorizing the label-generation formula, not learning financial behaviour).

This regressor learns non-linear interactions between salary, city cost index,
income growth rate, and timeline — what the classifier could not.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import KFold
from dataclasses import dataclass
from typing import Optional

from vestara.data.synthetic_data import generate_regression_dataset, REGRESSION_FEATURES


GREEN_BOUNDARY = 0.85   # predicted months < timeline × 0.85  → Green
YELLOW_BOUNDARY = 1.15  # timeline × 0.85 ≤ predicted < timeline × 1.15 → Yellow
# Red: predicted ≥ timeline × 1.15


@dataclass
class RegressionResult:
    verdict: str
    predicted_months: float
    user_timeline_months: int
    confidence: str  # HIGH >80%, MEDIUM 60-80%, LOW <60%
    months_surplus: float  # positive = ahead of schedule, negative = behind
    ratio_surplus: float   # predicted/timeline as ratio


class FeasibilityRegressor:
    FEATURES = REGRESSION_FEATURES

    def __init__(self):
        self._model: Optional[GradientBoostingRegressor] = None
        self._is_trained = False
        self._cv_rmse: Optional[float] = None
        self._cv_scores: list[float] = []

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    def train(self, n_samples: int = 5000) -> dict:
        df = generate_regression_dataset(n_samples)

        X = df[self.FEATURES]
        y = df["months_to_achieve_goal"]

        # 5-fold cross-validation
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        rmse_scores = []
        for fold, (train_idx, val_idx) in enumerate(kf.split(X)):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            model = GradientBoostingRegressor(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                min_samples_split=10,
                min_samples_leaf=5,
                random_state=42,
            )
            model.fit(X_train, y_train)
            preds = model.predict(X_val)
            rmse = np.sqrt(np.mean((preds - y_val) ** 2))
            rmse_scores.append(rmse)

        self._cv_rmse = float(np.mean(rmse_scores))
        self._cv_scores = [float(s) for s in rmse_scores]

        # Train final model on all data
        self._model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
        )
        self._model.fit(X, y)
        self._is_trained = True

        return {
            "cv_rmse": self._cv_rmse,
            "cv_scores": self._cv_scores,
            "feature_importance": self._feature_importance_dict(),
        }

    def predict_with_result(
        self,
        monthly_salary: float,
        city_living_cost_index: int,
        goal_cost: float,
        timeline_years: int,
        income_growth_rate: float,
        monthly_living_cost: float,
        disposable_income: float,
    ) -> RegressionResult:
        if not self._is_trained:
            raise RuntimeError("Model not trained. Call .train() first.")

        X = pd.DataFrame([{
            "monthly_salary": monthly_salary,
            "city_living_cost_index": city_living_cost_index,
            "goal_cost": goal_cost,
            "timeline_years": timeline_years,
            "income_growth_rate": income_growth_rate,
            "monthly_living_cost": monthly_living_cost,
            "disposable_income": disposable_income,
        }])

        predicted_months = float(self._model.predict(X)[0])
        user_timeline_months = timeline_years * 12

        # Post-processing: classify residual
        if predicted_months < user_timeline_months * GREEN_BOUNDARY:
            verdict = "green"
        elif predicted_months < user_timeline_months * YELLOW_BOUNDARY:
            verdict = "yellow"
        else:
            verdict = "red"

        months_surplus = user_timeline_months - predicted_months
        ratio_surplus = predicted_months / user_timeline_months

        # Confidence: based on RMSE relative to mean target
        mean_target = 120  # ~10 years in months as reference scale
        cv_rmse = self._cv_rmse or 50
        confidence_pct = max(0, min(1, 1 - (cv_rmse / mean_target)))
        if confidence_pct >= 0.80:
            confidence = "HIGH"
        elif confidence_pct >= 0.60:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        return RegressionResult(
            verdict=verdict,
            predicted_months=round(predicted_months, 1),
            user_timeline_months=user_timeline_months,
            confidence=confidence,
            months_surplus=round(months_surplus, 1),
            ratio_surplus=round(ratio_surplus, 4),
        )

    def _feature_importance_dict(self) -> dict:
        scores = self._model.feature_importances_
        return {col: float(round(score, 4)) for col, score in zip(self.FEATURES, scores)}


def save_model(regressor: FeasibilityRegressor, path: str) -> None:
    import pickle
    with open(path, "wb") as f:
        pickle.dump(regressor, f)


def load_model(path: str) -> FeasibilityRegressor:
    import pickle
    with open(path, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    clf = FeasibilityRegressor()
    metrics = clf.train(n_samples=5000)

    print("=== Regressor Training Complete ===")
    print(f"CV RMSE: {metrics['cv_rmse']:.1f} months")
    print(f"Per-fold RMSE: {[f'{s:.1f}' for s in metrics['cv_scores']]}")
    print("\nFeature Importance:")
    fi = sorted(metrics["feature_importance"].items(), key=lambda x: -x[1])
    for feat, score in fi:
        print(f"  {feat:35s}  {score:.4f}")

    # Test prediction
    result = clf.predict_with_result(
        monthly_salary=15_000_000,
        city_living_cost_index=8,
        goal_cost=2_100_000_000,
        timeline_years=10,
        income_growth_rate=0.08,
        monthly_living_cost=8_500_000,
        disposable_income=6_500_000,
    )
    print(f"\nTest prediction:")
    print(f"  Verdict: {result.verdict}")
    print(f"  Predicted months: {result.predicted_months}")
    print(f"  Timeline: {result.user_timeline_months} months")
    print(f"  Confidence: {result.confidence}")
    print(f"  Months surplus: {result.months_surplus}")

    import os
    os.makedirs("models", exist_ok=True)
    save_model(clf, "models/feasibility_regressor.pkl")
    print("\nSaved to models/feasibility_regressor.pkl")
