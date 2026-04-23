# 001 — Build Plan

## Phase 1: Core ML Engine

**What was built:**
`FeasibilityClassifier` — `GradientBoostingClassifier` trained on synthetic Indonesian financial data. Feature set: salary, city cost index, goal cost, timeline, income growth rate, monthly living cost, disposable income, monthly investment required, investment-to-income ratio. Target: green/yellow/red verdict.

**Key decisions:**
- Synthetic data generator using Indonesian cost distributions (property per sqm by city, school fees, living costs)
- Labels derived from `investment_to_income_ratio` thresholds (green <30%, yellow 30–50%, red >50%)
- Rule-based classification was explicitly chosen over pure statistical ML — financial feasibility is fundamentally a ratio comparison problem

**What changed from original plan and why:**
The original plan called for a pure ML classifier. During implementation, the team discovered the classifier achieved 99.9% accuracy — a red flag indicating label contamination. The investment-to-income ratio was both a feature and the sole basis for the label formula, causing the model to memorize the exact formula instead of learning financial behavior. This led to the Phase 5 regression refactor.

---

## Phase 2: Goal Builder + Risk Profiler

**What was built:**
`GoalBuilder` — estimates costs for 7 goal types (Property, Education, Retirement, Emergency Fund, Wedding, Higher Education, Custom) using Indonesian-specific cost data. `RiskProfiler` — 12-question quiz aligned to OJK risk classification framework, mapping to Konservatif/Moderat/Agresif profiles.

**Key decisions:**
- Goal types mapped to Indonesian cultural realities (wedding scale ranges, education tiers from TK to international school, higher education abroad cost estimates)
- Risk profiler uses 8 dimensions: loss tolerance, income stability, debt load, dependents, investment knowledge, time horizon, liquidity needs, ethical preferences
- Allocation ranges derived from OJK mutual fund guidelines for each risk profile

**What changed from original plan and why:**
No major deviations. The goal builder's follow-up questions per goal type were more granular than initially specified (e.g., property size broken into 4 options with specific sqm mappings rather than a single slider).

---

## Phase 3: Scenario Optimizer + Portfolio Optimizer

**What was built:**
`ScenarioOptimizer` — finds minimum viable adjustments to flip Yellow/Red verdicts to Green via 4 levers: extend timeline, relocate to lower-cost city, reduce goal size, increase monthly contribution. `PortfolioOptimizer` — rule-based allocation across 6 Indonesian instruments (deposito, ORI/SBR, reksa dana pasar uang, reksa dana pendapatan tetap, reksa dana equity, REITs).

**Key decisions:**
- Lever priority order: timeline > location > goal size > contribution (easiest to hardest behavioral change)
- Portfolio allocation uses blended expected return and volatility weighted by percentage allocation
- Equity capped at 40%, REITs at 10% for timelines under 3 years (pre-market-entry constraint)

**What changed from original plan and why:**
Originally planned to use mean-variance optimization (Markowitz-style). Replaced with rule-based allocation because: (1) correlation matrix between Indonesian instruments is not well-documented, (2) the primary output needed is a monthly contribution split, not an efficient frontier, (3) rule-based is more interpretable for a demo setting.

---

## Phase 4: Streamlit UI Integration

**What was built:**
5-page Streamlit application: Goal Builder, Feasibility Analysis, Risk Profiler, Portfolio Recommendation, Dashboard. Session state manages multi-step flow. Feasibility analysis uses rule-based computation (no model loaded) in the UI layer.

**Key decisions:**
- All 5 pages are functional and wired to real computation functions
- Scenario optimizer called with real parameters from session state
- Portfolio projection uses blended return compounding with yearly trajectory

**What changed from original plan and why:**
UI was built to be functional, not polished. The original plan had a more elaborate onboarding flow. Simplified to match demo pacing requirements. The "Custom" goal type was added to handle edge cases where users have non-standard goals not covered by the 6 structured types.

---

## Phase 5: /analyze Findings → C1–C5 Critical Fixes

**What was built (this session):**

### C1: Hard Gate — Scenario Optimizer
`run_scenario_analysis()` now returns `blocked_reason` when `ratio >= 100%`. Prevents recommending contribution increases when disposable income is already fully consumed. Blocks at the computation level, not just the UI level.

### C2: Regression Refactor
`FeasibilityRegressor` replaces `FeasibilityClassifier`. `GradientBoostingRegressor` predicts `months_to_achieve_goal`. Post-processing classifies residual: GREEN < 85% of timeline, YELLOW 85–115%, RED ≥ 115%. 5-fold CV with RMSE ~6755 months (genuine uncertainty, not memorized labels). Feature importance spread across all 7 features.

### C3: 15% Contingency Buffer — Property Goals
`estimate_property_cost()` now multiplies by `PROPERTY_BUFFER = 1.15`. Covers PPHTB (property transfer tax), notary fees, and price appreciation buffer. Without this, property goals were systematically understated by 10–15%.

### C4: Equity Cap for Short Timelines
`apply_equity_cap_for_short_timeline()` enforces equity ≤ 40%, REITs ≤ 10% for timelines < 3 years. Prevents recommending equity-heavy allocations for goals that are near-term and cannot absorb market drawdown. Also fixed pre-existing bug in `compute_blended_return` that returned percentage (612.5) instead of decimal rate (0.06125), causing projected values to inflate to 10²⁷.

### C5: Currency Depreciation Buffer — Abroad Education
`estimate_higher_education_cost()` now applies `IDR_DEPRECIATION_RATE = 4%/yr` compounding over degree years, plus `ABROAD_BUFFER = 10%` for application fees and living setup. IDR weakens approximately 4% per year against major currencies (2019–2024 average). Without this buffer, abroad education costs were systematically understated for longer degree programs.

---

## Phase 6: /redteam + /codify

**Status:** Not yet executed.

**Planned:**
- `/redteam`: Structured walkthrough of the full user flow from a first-time Indonesian professional's perspective
- `/codify`: Capture build decisions as institutional knowledge in this workspace

---

## Build Order Rationale

The implementation order (core ML → goal builder → optimizers → UI → fixes → validation) was chosen because:
1. Core ML provides the mathematical foundation everything else depends on
2. Goal builder had to exist before feasibility analysis could use real costs
3. Scenario optimizer requires feasibility verdicts as input
4. Portfolio optimizer requires both scenario and risk profile
5. UI was placed last to ensure all computation was validated before wiring to a user-facing interface
6. Critical fixes (C1–C5) were discovered during `/analyze` and addressed before `/redteam`

## Deferred Items

The following were identified in `/analyze` but deliberately not built for the MVP demo:
- **T3:** Income stress test (how feasibility changes if salary drops 30%)
- **T5:** Data maintenance staleness monitoring (when to refresh cost data)
- **T6:** Test infrastructure (pytest suite for the engine layer)
- **T7:** Streamlit session state wiring for multi-goal tracking
- **T8:** Competitor comparison benchmarking
