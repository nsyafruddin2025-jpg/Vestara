# Synthetic Data Limits and Model Weaknesses

## What the ML Model Actually Does

Vestara has two "models":

### 1. Feasibility Classifier
**Type:** Rule-based threshold (not ML)
**Input:** Monthly salary, city, goal cost, timeline
**Output:** Green / Yellow / Red verdict based on 30/50% investment-to-disposable ratio

**Why not ML:**
- No labelled data: we don't know which real users' goals were achieved
- Regulatory: a rule-based system is transparent and auditable
- Sufficient: the 30/50% thresholds are conservative and defensible

### 2. Feasibility Classifier (actual ML model, `feasibility_classifier.pkl`)
**What it was supposed to do:** Use trained ML model instead of rule-based threshold.
**Why it doesn't run in this environment:** `sklearn` not available in production Streamlit env.
**Current behaviour:** Falls back to rule-based threshold.
**Gap:** The trained model (in `models/feasibility_classifier.pkl`) exists but is not used.

---

## Synthetic Data Limitations

### Property Cost Data

| Source | Quality | Gap |
|--------|---------|-----|
| City-level price per sqm | Public data, reasonably accurate | No neighbourhood-level granularity |
| Landed house premium | 30% estimate | Actual range 20-40%, varies by area |
| Building vs land split | Assumed ratios | Not validated against real transactions |
| Buffer (15% for fees) | Industry estimate | Accurate for most transactions |

**Biggest risk:** A user targeting a specific neighbourhood in South Jakarta could be Rp 200M+ off if the neighbourhood is significantly above or below the city average.

**Mitigation in place:** Data freshness warning warns of &#177;15-20% uncertainty.

### Living Cost Data

| Source | Quality | Gap |
|--------|---------|-----|
| City-level monthly living costs | Public data, reasonably accurate | Doesn't capture lifestyle variation |
| No individual categorisation | Fixed per city | High-income user in Bandung same as low-income |

**Biggest risk:** Disposable income calculation uses city average, not user's actual spending.

### Return Assumptions

| Instrument | Assumption | Source | Risk |
|-----------|-----------|--------|------|
| Deposito | 4.5% | LPS rate, conservative | Accurate |
| ORI/SBR | 6.5% | Government bond average | Accurate |
| Reksa Dana Pasar Uang | 5.5% | Money market fund average | Conservative |
| Reksa Dana Pendapatan Tetap | 7.5% | Bond fund average | Conservative |
| Reksa Dana Saham | 12% | Equity fund historical avg | Conservative |
| DIRE/REITs | 10% | Property fund average | Conservative |

**Assessment:** All assumptions err on the side of caution. Real returns could be higher or lower. This is deliberate — Vestara would rather under-promise than over-promise.

### Risk Profile

The 12-question risk profiler is的理论-based, not behavioural-data-validated. The questions are designed to elicit risk tolerance but haven't been A/B tested or calibrated against real investor behaviour.

**Known weakness:** Users who are risk-averse in theory may behave differently when their portfolio drops 20%. The risk profiler doesn't account for this.

---

## Model Weaknesses Summary

| Weakness | Severity | Can fix without real data? |
|----------|----------|---------------------------|
| Property costs city-level only | Medium | Partially (add neighbourhood API) |
| Living costs city-level only | Low | Partially (add expense input) |
| Return assumptions static | Low | Yes (add regime-aware assumptions) |
| Risk profiler not validated | Medium | Partially (add user feedback loop) |
| No ML model in production | High | No (needs real outcome data) |
| No inflation adjustment | Medium | Yes (add CPI projection) |
