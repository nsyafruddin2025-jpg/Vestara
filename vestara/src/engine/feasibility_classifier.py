"""
Feasibility Engine — XGBoost classifier.
Predicts green / yellow / red verdict for a goal given user financial profile.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix

from vestara.data.synthetic_data import generate_synthetic_dataset, TRAINING_FEATURES

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
        """Generate synthetic data, train XGBoost, return metrics."""
        df = generate_synthetic_dataset(n_samples)

        X = df[self._feature_cols]
        y_raw = df["verdict"]

        self._label_encoder.fit(VERDICT_ORDER)
        y = self._label_encoder.transform(y_raw)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        scale_pos_weight = self._compute_scale_pos_weight(y_train)

        self._model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            objective="multi:softmax",
            num_class=3,
            scale_pos_weight=scale_pos_weight,
            eval_metric="mlogloss",
            use_label_encoder=False,
            random_state=42,
            n_jobs=-1,
        )

        self._model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False,
        )

        y_pred = self._model.predict(X_test)
        y_pred_labels = self._label_encoder.inverse_transform(y_pred)
        y_test_labels = self._label_encoder.inverse_transform(y_test)

        report = classification_report(y_test_labels, y_pred_labels, output_dict=True)
        cm = confusion_matrix(y_test_labels, y_pred_labels, labels=VERDICT_ORDER)

        self._is_trained = True

        return {
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "n_train": len(X_train),
            "n_test": len(X_test),
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

    def _compute_scale_pos_weight(self, y: np.ndarray) -> dict:
        """Compute per-class weights for imbalanced data."""
        counts = pd.Series(y).value_counts()
        total = len(y)
        weights = {}
        for cls_idx, cnt in counts.items():
            weights[cls_idx] = total / (3 * cnt)
        return weights

    def _feature_importance_dict(self) -> dict:
        scores = self._model.feature_importances_
        return {col: float(round(score, 4)) for col, score in zip(self._feature_cols, scores)}


def save_model(classifier: FeasibilityClassifier, path: str) -> None:
    import pickle
    with open(path, "wb") as f:
        pickle.dump(classifier, f)


def load_model(path: str) -> FeasibilityClassifier:
    import pickle
    with open(path, "rb") as f:
        return pickle.load(f)


if __name__ == "__main__":
    clf = FeasibilityClassifier()
    metrics = clf.train(n_samples=5000)

    print("=== Training Complete ===")
    print(f"Train: {metrics['n_train']} | Test: {metrics['n_test']}")
    print(f"\nClassification Report:\n{classification_report(metrics['classification_report'])}")
    print(f"\nConfusion Matrix:\n{np.array(metrics['confusion_matrix'])}")
    print(f"\nFeature Importance:\n{metrics['feature_importance']}")

    save_model(clf, "vestara/models/feasibility_classifier.pkl")
    print("\nModel saved to vestara/models/feasibility_classifier.pkl")
