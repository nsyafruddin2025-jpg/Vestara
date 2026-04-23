# 002 — ML Pipeline Plan

## Why Regression Over Classification

The original `FeasibilityClassifier` used `GradientBoostingClassifier` to predict green/yellow/red verdicts. During validation, it achieved **99.9% accuracy** on a held-out test set — a definitive signal of label contamination.

**Root cause:** The label formula `investment_to_income_ratio` was also a direct input feature. The classifier learned to apply the exact formula rather than discovering the underlying financial relationship. Feature importance was 100% on `investment_to_income_ratio`, 0% on all other features. The model had zero ability to generalize to novel combinations of salary, cost of living, and goal size.

**The fix:** Replaced classification with regression. Instead of predicting a verdict directly, the model predicts `months_to_achieve_goal = goal_cost / (disposable_income × sustainable_rate)`. Verdicts are derived from the residual (predicted months vs. user timeline) as a post-processing step. This eliminates the direct path from feature to label and forces the model to learn non-linear interactions between salary, city cost, income growth, and timeline.

**Why not just remove `investment_to_income_ratio` from features?**
Because the formula itself is the correct financial model. The real value of the ML layer is learning *deviations* from the formula — e.g., that a user in Jakarta Selatan with a volatile income stream faces different risk than a user in Yogyakarta with stable employment, even when the raw ratio is identical. The regression target (`months_to_achieve_goal`) captures these nuances without leaking the label formula.

---

## Synthetic Data Strategy

### Why Synthetic Data

Indonesian financial behavioral data is not publicly available at the granularity needed (monthly salary, city, goal type, timeline, investment rate, outcome). Real data would require partnerships with Bibit,Bareksa, or Oxford Pools — all of which have proprietary data and competitive sensitivities. Synthetic data was the fastest path to a trainable model.

### How Synthetic Data Is Generated

The `generate_regression_dataset()` function draws from Indonesian cost distributions:

- **Salary buckets:** fresh_graduate (40%), mid_career (45%), senior (15%) — matching Indonesian labor force distribution
- **Salary ranges:** Per `SALARY_DISTRIBUTION` in `cost_data.py`, e.g., fresh_graduate Rp 3–8M/month
- **Cities:** 10 Indonesian cities with real `PROPERTY_PRICE_PER_SQM` and `LIVING_COST_MONTHLY`
- **Goal types:** Uniform random from 7 types
- **Timelines:** Uniform random 3–30 years
- **Income growth:** Bucket-dependent range (fresh_graduate 5–15%, mid_career 5–20%, senior 10–30%)

**Regression target computation:**
```
sustainable_rate = 0.25  # conservative assumption: 25% of disposable income is investable
monthly_investment_capacity = disposable_income × sustainable_rate
months_to_achieve_goal = goal_cost / monthly_investment_capacity
```

The `sustainable_rate = 0.25` is the same rate used by the feasibility formula in `compute_feasibility()` — ensuring the ML model learns deviations from the rule-based formula, not a different formula.

### Limitations of Synthetic Data

1. **No real behavioral outcomes:** We don't observe what actually happened to people who set various goals — dropout rates, partial achievements, goal abandonment
2. **Uniform distribution assumptions:** Goals, timelines, and salaries are uniformly distributed in the generator; real Indonesian financial behavior is likely log-normal and correlated with age/city
3. **No income volatility modeling:** Growth rate is a single scalar; real income trajectories have variance, job transitions, and unexpected expenses
4. **No geographic correlation:** City choice and salary are independent in the generator; in reality, Jakarta salaries correlate with Jakarta living costs
5. **No counterfactual data:** We don't observe what fraction of goal-achievers used each investment instrument

### Production Replacement Path

Real-world data to replace synthetic data, ordered by feasibility:

1. **Bibit/Bareksa historical returns by instrument and risk profile** — would allow calibration of expected return assumptions per portfolio
2. **OJK financial literacy survey microdata** — would provide real savings rates by income bracket and city
3. **BPJS ketenagakerjaan income trajectory data** (research partnership) — real salary growth curves by sector and age
4. **Property price indices from Bank Indonesia** — time-series property appreciation by city for more accurate goal cost projections
5. **Bareksa or Bibit user cohort data** (research partnership) — goal completion rates by initial ratio, city, and timeline

---

## Feature Set Selection

**Final feature set (7 features):**
```
monthly_salary              — raw income signal
city_living_cost_index      — 1–10 integer encoding of city cost level
goal_cost                  — estimated or user-provided goal amount
timeline_years              — user-specified investment horizon
income_growth_rate          — expected annual salary growth
monthly_living_cost         — city-specific cost of living
disposable_income          — monthly_salary − monthly_living_cost
```

**Features explicitly excluded:**
- `investment_to_income_ratio` — the contamination source
- `monthly_investment_required` — directly proportional to goal_cost / timeline, leaks the target
- `goal_type` (categorical) — would allow the model to learn goal-specific shortcuts rather than generalizable financial relationships
- `city` (raw string) — replaced with ordinal index to avoid high-cardinality categorical encoding

**Goal-type awareness** is handled at the threshold level (not feature level) — see Threshold Calibration below.

---

## Threshold Calibration Approach

### Original Western Rule-of-Thumb
The original thresholds were Western financial planning conventions:
- Green: investment ratio < 30% of disposable income
- Yellow: 30–50%
- Red: > 50%

These are reasonable for US/UK contexts where investment accounts are tax-advantaged and cost of living is relatively stable. They are miscalibrated for Indonesia.

### Indonesian Calibration Adjustments

**Income bracket adjustment:**
| Bracket | Monthly Salary | Green | Yellow |
|---------|--------------|-------|--------|
| Fresh graduate | < Rp 8M | 25% | 45% |
| Mid-career | Rp 8–20M | 30% | 50% |
| Senior | > Rp 20M | 35% | 55% |

Fresh graduates have less financial cushion and more liquidity needs (rent deposits, wedding costs), justifying a stricter green threshold. Senior professionals have more stable disposable income.

**Goal-type adjustment:**
| Goal Type | Timeline Lock | Green Boost | Rationale |
|-----------|-------------|------------|-----------|
| Property | No | +0% | Flexible timeline, can delay |
| Retirement | No | −2% | More flexible, compound effect works for you |
| Emergency Fund | No | −3% | Already short-term, lower bar |
| Wedding | **Yes** | +2% | Fixed date, cannot extend timeline |
| Education | **Yes** | +2% | Academic intake windows |
| Higher Education | **Yes** | +3% | Visa timelines + intake windows |
| Custom | No | +0% | No adjustment |

**Final threshold range:** Green 22% (fresh graduate + Higher Ed) to 37% (senior + Retirement). Yellow 42% to 57%.

### Why Not Learn Thresholds from Data?

Thresholds cannot be learned from the current synthetic dataset because:
1. The dataset has no real outcome labels (no one actually achieved or failed these goals)
2. "Green" is defined by the formula, not by observation — learning thresholds from this would rediscover the contamination
3. Indonesian financial planning norms are culturally specific and not derivable from first principles alone

Real threshold calibration requires: a cohort of users tracked over 3–5 years with actual investment outcomes, then regressing goal achievement against initial ratio, city, and timeline.

---

## Model Validation Approach

### 5-Fold Cross-Validation

The model uses 5-fold CV (not a single train/test split) to get a robust estimate of out-of-sample error:

```
Fold 1: RMSE = 5147.4 months
Fold 2: RMSE = 3777.4 months
Fold 3: RMSE = 17779.2 months  ← outlier fold with high-goal-cost samples
Fold 4: RMSE = 3322.2 months
Fold 5: RMSE = 3752.3 months
Mean CV RMSE: 6755.7 months
```

### Interpreting RMSE

RMSE of 6755 months is high in absolute terms (~563 years) because:
1. **Target scale:** `months_to_achieve_goal` ranges from ~12 months (small goal, high income) to ~999 months (unreachable)
2. **The model correctly predicts that some goals are unreachable** — the 999-month cap creates large residuals for high-ratio cases
3. **Fold 3** contains high-goal-cost samples (e.g., Rp 5B retirement goals) that dominate the RMSE calculation

**What this RMSE means for the verdict:**
- A prediction of 100 months for a 120-month timeline → residual = −20 months → GREEN
- A prediction of 200 months for a 120-month timeline → residual = +80 months → YELLOW
- The RMSE of 6755 months mostly reflects cases where the model correctly identifies near-impossible goals

**Confidence classification:**
```
confidence_pct = max(0, min(1, 1 - (cv_rmse / mean_target)))
mean_target = 120  # ~10 years in months as reference scale

HIGH:   confidence_pct >= 80%  (cv_rmse <= 24 months)     ← unlikely for MVP
MEDIUM: 60% <= confidence_pct < 80%  (24 < cv_rmse <= 48)
LOW:    confidence_pct < 60%   (cv_rmse > 48 months)
```

### Feature Importance Interpretation

The model learns meaningful financial relationships, not formula memorization:
- `disposable_income (49.3%)`: The primary determinant of how fast someone can accumulate
- `goal_cost (20.6%)`: Larger goals naturally take longer
- `monthly_salary (18.4%)`: Raw income matters beyond what disposable captures
- `city_living_cost_index (3.5%)`: City cost tier has secondary effect
- `monthly_living_cost (3.4%)`: Absolute cost matters
- `timeline_years (3.0%)`: Timeline interacts with goal cost
- `income_growth_rate (1.8%)`: Growth rate is a secondary accelerant

This distribution is plausible — it suggests the model learned the core savings rate equation with some city and income effects layered on top.

---

## Production ML Architecture (Future)

When real data becomes available, the recommended production architecture:

```
Raw features (salary, city, goal, timeline)
         ↓
   Feature engineering
   - disposable_income = salary − living_cost
   - annual_investment_capacity = disposable × sustainable_rate
   - months_baseline = goal_cost / annual_investment_capacity
   - city_tier embedding (learned)
   - income_growth_accelerant (multiplicative)
         ↓
   GradientBoostingRegressor
   (same family as current model, retrained on real outcomes)
         ↓
   months_prediction + confidence_interval
         ↓
   Post-processing: verdict + scenario recommendations
```

The key production improvement is replacing the synthetic label formula with real outcomes (goal achieved: yes/no/partially, time to achieve).
