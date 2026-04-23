# C2: Refactor Feasibility Classifier — Classification → Regression

## Problem

The current GradientBoostingClassifier achieves 99.9% accuracy because its training labels are derived from the same `investment_to_income_ratio` formula used as the primary feature. The model memorizes the label rule, learns nothing generalizable, and `investment_to_income_ratio` has 100% feature importance while all other features are 0%.

## Spec

Implements: `specs/feasibility.md` § "Refactor Architecture" and `specs/synthetic-data.md` § "Minimum Defensibility Requirements"

## Changes

### `vestara/src/engine/feasibility_regression.py` (new file)

Build a new `FeasibilityRegressor` class:

1. Use `GradientBoostingRegressor` (sklearn, same family as current classifier)
2. Target: `months_to_achieve_goal = goal_cost / monthly_investment_capacity`
   where `monthly_investment_capacity = disposable × sustainable_rate` (use 0.25 as conservative default)
3. Features (8, no `investment_to_income_ratio` to avoid contamination):
   - `monthly_salary`
   - `city_living_cost_index`
   - `goal_cost`
   - `timeline_years`
   - `income_growth_rate`
   - `monthly_living_cost`
   - `disposable_income`
   - `annual_idr_depreciation` (for abroad education; 0 for domestic goals)
4. Post-processing classifier: compare `predicted_months` vs `user_timeline`
   - Green: `predicted_months < timeline × 0.85`
   - Yellow: `timeline × 0.85 ≤ predicted_months < timeline × 1.15`
   - Red: `predicted_months ≥ timeline × 1.15`
5. Validation: 5-fold stratified CV (NOT single split); report RMSE, MAE, per-fold metrics
6. Feature importance target: spread across all 8 features, not dominated by one

### Update `vestara/data/synthetic_data.py`

Add a `generate_regression_dataset()` function:

- Same base data as existing `generate_synthetic_dataset()`
- Add `months_to_achieve_goal = goal_cost / (disposable × 0.25)` as target column
- Add `annual_idr_depreciation` column (0 for domestic, 0.04 for abroad education)
- Generate 5,000 samples, save to `synthetic_regression_data.csv`

### `vestara/src/engine/feasibility_classifier.py`

Add a `predict_with_confidence()` method to the existing `FeasibilityClassifier`:

- Return `{"verdict": ..., "confidence": ..., "months_predicted": ..., "months_required": ...}`
- Use prediction variance across trees as confidence proxy

### `vestara/src/engine/__init__.py`

Export both `FeasibilityClassifier` and `FeasibilityRegressor`

### `vestara/src/ui/app.py` (Feasibility page)

Update to call `predict_with_confidence()` and display:

- Verdict badge
- "Model estimates [X] months needed; your timeline is [Y] years"
- Confidence indicator: HIGH (>80%), MEDIUM (60-80%), LOW (<60%)

## Tests

`tests/unit/test_feasibility_regression.py`:

- `test_regressor_feature_importance_not_dominated_by_single_feature()`: after training, no single feature > 60% importance
- `test_regressor_kfold_cv_rmse()`: RMSE should be > 0 (not perfect)
- `test_postprocessing_classifier_boundaries()`: test the 0.85/1.15 boundary logic
- `test_prediction_includes_confidence()`: result dict has confidence key

## Constraints

- Keep existing `FeasibilityClassifier` intact during transition — add new regressor as parallel class
- Do not add `investment_to_income_ratio` as a feature in the regression model (preserves contamination)
- k-fold CV is required, not optional
- Present both old (classifier) and new (regressor) results in the UI during transition
