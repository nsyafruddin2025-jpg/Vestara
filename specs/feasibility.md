# Feasibility Engine — Spec

## Current Implementation

GradientBoostingClassifier (sklearn, XGBoost-family) trained on 5,000 synthetic samples.
9 features: monthly_salary, city_living_cost_index, goal_cost, timeline_years,
income_growth_rate, monthly_living_cost, disposable_income, monthly_investment_required,
investment_to_income_ratio.
Verdicts: green (<30%), yellow (30-50%), red (>50%).

## CRITICAL FINDING: Refactor Required

Current model achieves **99.9% training accuracy** because labels are derived from
the same formula as the primary feature (investment_to_income_ratio). The model
is memorizing `if ratio < 0.30 → green` — ML adds zero value over the rule.

investment_to_income_ratio has 100% feature importance. All other features are 0%.

## Refactor Architecture (Required Before Demo)

```
Step 1: Regression model
  Input: monthly_salary, city_living_cost_index, goal_cost, timeline_years,
         income_growth_rate, monthly_living_cost
  Output: predicted_months_to_achieve_goal (continuous)

Step 2: Post-processing classifier
  Compare predicted_months vs user's stated timeline
  Green:  predicted_months < timeline × 0.85
  Yellow: timeline × 0.85 ≤ predicted_months < timeline × 1.15
  Red:    predicted_months ≥ timeline × 1.15

This lets the ML learn non-linear interactions between income growth rate,
city cost index, and timeline that a simple ratio formula cannot capture.
```

## Feature Importance Target (Post-Refactor)

After refactor, expected meaningful feature contributions:

- monthly_salary + income_growth_rate: 30-40% combined
- goal_cost / timeline_years interaction: 20-30%
- city_living_cost_index: 15-25%
- monthly_living_cost: 10-15%

If investment_to_income_ratio still dominates post-refactor, the model is still
memorizing — return to regression form and audit the feature set.

## Validation Protocol

- k-fold cross-validation (k=5), not single train/test split
- Adversarial validation: synthetic data vs real reference distributions
- Per-class F1 scores, not accuracy (imbalanced classes)
- Confusion matrix with all 3 classes reported
- Boundary case test: users near 30% and 50% thresholds
- Out-of-sample Indonesian profiles: test against manual calculations
  for 10 representative user profiles (mix of income brackets, cities, goal types)

## Threshold Calibration

See `threshold-calibration.md` for full spec. Current thresholds (30/50) are
business judgment calls, not empirically grounded. Income-bracket calibration
is a known gap.
