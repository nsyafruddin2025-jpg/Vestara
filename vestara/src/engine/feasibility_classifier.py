"""
Feasibility Engine — Gradient-boosted classifier (sklearn).
Predicts green / yellow / red verdict for a goal given user financial profile.
Uses sklearn GradientBoostingClassifier — gradient-boosted trees, same family as XGBoost.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from vestara.data.synthetic_data import generate_synthetic_dataset

VERDICT_ORDER = ["green", "yellow", "red"]


class FeasibilityClassifier:
    def __init__(self):
        self._model = None
        self._label_encoder = LabelEncoder()
        self._feature_cols = [
            "monthly_salary",
            "city_living_cost_index",
            "goal_cost",
            "timeline_years",
            "income_growth_rate",
            "monthly_living_cost",
            "disposable_income",
            "monthly_investment_required",
            "investment_to_income_ratio",
        ]
        self._is_trained = False

    @property
    def is_trained(self) -> bool:
        return self._is_trained

    def train(self, n_samples: int = 5000, test_size: float = 0.2) -> dict:
        df = generate_synthetic_dataset(n_samples)

        X = df[self._feature_cols]
        y_raw = df["verdict"]

        self._label_encoder.fit(VERDICT_ORDER)
        y = self._label_encoder.transform(y_raw)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        self._model = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42,
        )

        self._model.fit(X_train, y_train)

        y_pred = self._model.predict(X_test)
        y_pred_labels = self._label_encoder.inverse_transform(y_pred)
        y_test_labels = self._label_encoder.inverse_transform(y_test)

        report = classification_report(
            y_test_labels, y_pred_labels, labels=VERDICT_ORDER, output_dict=True
        )
        cm = confusion_matrix(y_test_labels, y_pred_labels, labels=VERDICT_ORDER)

        self._is_trained = True

        return {
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "n_train": len(X_train),
            "n_test": len(X_test),
            "accuracy": accuracy_score(y_test, self._model.predict(X_test)),
            "feature_importance": self._feature_importance_dict(),
        }

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self._is_trained:
            raise RuntimeError("Model not trained yet. Call .train() first.")
        preds = self._model.predict(X)
        return self._label_encoder.inverse_transform(preds)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not self._is_trained:
            raise RuntimeError("Model not trained yet. Call .train() first.")
        return self._model.predict_proba(X)

    def _feature_importance_dict(self) -> dict:
        scores = self._model.feature_importances_
        return {col: float(round(score, 4)) for col, score in zip(self._feature_cols, scores)}


def save_model(classifier: "FeasibilityClassifier", path: str) -> None:
    import pickle
    with open(path, "wb") as f:
        pickle.dump(classifier, f)


def load_model(path: str) -> "FeasibilityClassifier":
    import pickle
    with open(path, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    clf = FeasibilityClassifier()
    metrics = clf.train(n_samples=5000)

    print("=== Training Complete ===")
    print(f"Train: {metrics['n_train']} | Test: {metrics['n_test']}")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"\nClassification Report:")
    for label in VERDICT_ORDER:
        r = metrics["classification_report"][label]
        print(f"  {label:8s}  precision={r['precision']:.3f}  recall={r['recall']:.3f}  f1={r['f1-score']:.3f}")
    print(f"\nConfusion Matrix:")
    print(f"            green   yellow     red")
    cm = np.array(metrics["confusion_matrix"])
    for label, row in zip(VERDICT_ORDER, cm):
        print(f"  {label:8s}  {row[0]:6d}   {row[1]:6d}   {row[2]:6d}")
    print(f"\nFeature Importance:")
    fi = sorted(metrics["feature_importance"].items(), key=lambda x: -x[1])
    for feat, score in fi:
        print(f"  {feat:35s}  {score:.4f}")

    import os
    os.makedirs("models", exist_ok=True)
    save_model(clf, "models/feasibility_classifier.pkl")
    print("\nModel saved to models/feasibility_classifier.pkl")
