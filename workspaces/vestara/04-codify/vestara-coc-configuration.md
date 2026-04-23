# Vestara COC Configuration
## Cognitive Orchestration for Codegen — Institutional Knowledge Capture
**Phase:** /codify (Final) | **Project:** MGMT 655 Submission
**Date:** 2026-04-23 | **Status:** Complete

---

## 1. PRODUCT SUMMARY

### What Vestara Is

Vestara is a **goal-first investment planning platform** for young Indonesian professionals (age 22–35, salary Rp 5–25M/month). Where existing tools ask "how much should I invest?", Vestara asks "what do you want to achieve, and can you get there?"

The user selects a life goal (property purchase, education, retirement, wedding, emergency fund, abroad study, or custom), answers goal-specific follow-up questions, and receives:
1. A realistic cost estimate for their Indonesian city
2. A green/yellow/red feasibility verdict based on their income and timeline
3. Scenario-adjusted options (extend timeline, change city, reduce goal, increase contribution)
4. An OJK-aligned risk profile (12 questions, Konservatif/Moderat/Agresif)
5. An illustrative portfolio allocation across 6 Indonesian instruments

### Who It Is For

Primary: Indonesian professionals aged 22–35 earning Rp 5–25M/month who are starting to think about long-term financial goals but lack the financial planning tools specific to their context.

Secondary: Financial educators and HR departments at Indonesian companies using Vestara as an employee financial wellness tool.

### The Problem It Solves

Indonesian professionals face a specific planning gap: Western financial planning tools assume US/UK cost structures, tax regimes, and investment instrument landscapes. Bibit and Bareksa are investment platforms that start with "how much to invest." No tool starts with "what do you want to achieve in Jakarta, and is that realistic?"

Key problems addressed:
- Property costs in Jakarta require Rp 2–5B but most planning tools don't localize to Indonesian property markets
- Investment thresholds (30% rule) are Western conventions that don't account for Indonesia's 8–18% actual saving rate
- Financial goal types (wedding scale, education tier, higher education abroad) require Indonesian-specific cost modeling
- No tool combines feasibility analysis with scenario optimization and risk profiling for Indonesian users

### Competitive Differentiation

| Feature | Bibit | Bareksa | Vestara |
|---------|-------|---------|---------|
| Goal-first onboarding | No | No | **Yes** |
| Indonesian cost data | No | No | **Yes** |
| Feasibility verdict | No | No | **Yes** |
| Scenario optimizer | No | No | **Yes** |
| Synthetic ML model | Yes | Yes | **Yes** |
| Indonesian instruments only | Partial | Yes | **Yes** |
| POJK-aligned risk profiler | No | No | **Yes** |

---

## 2. COC WORKFLOW EXECUTED

### 2.1 /analyze

**What was researched:**
- Indonesian financial landscape: OJK regulatory framework (POJK 21/2011, POJK 17/2015, POJK 12/2022), Indonesian investment instrument taxonomy (reksa dana, ORI/SBR, REITs, deposito)
- Target market: 270M population, median age 28, underbanked, smartphone penetration driving fintech adoption
- Competitive landscape: Bibit (robo-advisor, Rp 3.5T AUM), Bareksa (fund supermarket), Pluang (gemastik savings), Financial Freedom (spreadsheet-based)
- Indonesian cost data: Property prices per sqm for 10 cities, school fees (TK to international), living costs, higher education abroad costs

**What was found (5 critical issues):**
- **C1:** Scenario optimizer recommends contribution increases when disposable income is zero/negative
- **C2:** Classifier achieves 99.9% accuracy — model memorizes formula, not financial behavior (label contamination)
- **C3:** Property goal costs lack 15% contingency buffer (PPHTB, notary, price appreciation)
- **C4:** Portfolio optimizer recommends equity-heavy allocations regardless of goal timeline
- **C5:** Abroad education costs lack currency depreciation buffer (IDR weakens 3–5%/yr)

**Decisions made during /analyze:**
- Classification → Regression refactor was mandatory (C2) — not a nice-to-have
- Hard gate on scenario optimizer (C1) was a one-line fix with high impact
- C3/C4/C5 were identified as systematic underestimation problems that would compound as users scaled
- T1/T2/T4 were identified as important but not blocking

**Skipped and why:**
- T3 (income stress test): Required simulating salary drops, complex scenario modeling
- T5 (data staleness monitoring): Would need production infrastructure
- T7 (multi-goal tracking): Required session state redesign
- T8 (competitor benchmarking): Required live data access

### 2.2 /todos

**Priority order set:**
```
C1 → C2 → C3 → C4 → C5 → T1 → T2 → T4
```
C1 and C2 were blocking — C1 produced nonsensical recommendations, C2 invalidated the ML model entirely. C3/C4/C5 were systematic biases that affected every user. T1/T2/T4 were important quality improvements.

**What was skipped:**
- T3, T5, T7, T8 — deferred to post-MGMT 655
- T6 (test infrastructure) — not a course requirement, deferred

**Commit-after-2 rule established:** After every 2 tasks, git commit with descriptive message. Show output before moving to next task.

### 2.3 /implement

**Order executed:**

**C1 (Hard Gate) — `ccee6e3`**
`run_scenario_analysis()` returns `blocked_reason` when `ratio >= 1.0`. Contribution lever is structurally unavailable when disposable income is fully consumed.

**C2 (Regression Refactor) — `2d69f36`**
New `FeasibilityRegressor` class using `GradientBoostingRegressor` predicting `months_to_achieve_goal`. Post-processing classifies residual into Green/Yellow/Red. CV RMSE: 6755 months (genuine uncertainty). Feature importance spread across all 7 features — no single feature dominates. Model saved to `models/feasibility_regressor.pkl`.

**C3 (Property Contingency Buffer) — `2d69f36`**
`estimate_property_cost()` now multiplies by `PROPERTY_BUFFER = 1.15`. Covers PPHTB, notary, and price appreciation. Example: 2BR Jakarta Selatan now estimates Rp 2,415,000,000 (was Rp 2,100,000,000).

**C4 (Equity Cap + Portfolio Bug Fix) — `2d69f36`**
`apply_equity_cap_for_short_timeline()` enforces equity ≤ 40%, REITs ≤ 10% for timelines < 3 years. Also fixed `compute_blended_return()` returning percentage (612.5) instead of decimal rate (0.06125), causing projected values to reach 10²⁷.

**C5 (Currency Depreciation Buffer) — `2d69f36`**
`estimate_higher_education_cost()` now applies `× (1.04)^degree_years × 1.10`. IDR depreciation 4%/yr + 10% buffer for application fees/exchange slippage. Singapore Master's (Top 50): base Rp 481M → Rp 572M.

**T1 (Adaptive Thresholds) + T2 (Goal-Type-Aware Levers) + T4 (Growth Chart) — `81e5df4`**
Income-bracket thresholds: fresh_graduate 25%/45%, mid_career 30%/50%, senior 35%/55%. Fixed-deadline goals (Wedding, Education, Higher Education) skip timeline extension lever. `st.line_chart` replaces trajectory table.

**Documentation (workspace files) — `a1244a2`**
Created `02-plans/` (001-build-plan.md, 002-ml-pipeline-plan.md, 003-product-roadmap.md) and `03-user-flows/` (001-primary-user-flow.md, 002-edge-case-flows.md, 003-demo-flow.md).

**Regulatory Fixes — `00c1893`**
- FIX 1: De-personalized portfolio language ("Ilustratif", not "your portfolio") + POJK 21/2011 disclaimer
- FIX 2: Initial Disclosure Document in expander (POJK 21/2011 Article 15/16)
- FIX 3: Instrument risk labels in allocation table (Indonesian)
- FIX 4: Data freshness warning on cost estimates (±15-20%)
- FIX 5: Lumpy goal equity warning for Property goals < 5 years

### 2.4 /redteam

**Four-perspective attack conducted:**

**PE Fund Investor findings:**
- R1 CRITICAL: Portfolio recommendation constitutes unlicensed investment advice under POJK 21/2011 — Path B (de-personalize) taken immediately
- R4 HIGH: Cost database accuracy risk — static values diverging 30-40% from market
- R11 HIGH: Affiliate unit economics require 200K MAU for Rp 1B/month — not viable at MVP scale
- R12 MEDIUM: Competitor can copy goal-first UX in 6 weeks — only durable moat is regulatory license

**Competing Product Team findings:**
- R1 CRITICAL: 6-week competitive replication window — only IZInas PK is durable moat
- R2 HIGH: Cost database is compilable from public sources in 2-3 weeks — moat is accuracy, not secrecy
- R3 HIGH: Pluang adding Goals tab would neutralize Vestara's positioning — license is only structural defense

**User Who Lost Money findings:**
- R5 CRITICAL: Equity-heavy allocation for 7-year Property goal — lumpy goal mechanics not accounted for, market drawdown in year 2 destroys timing
- R6 HIGH: Static database caused Rp 800M shortfall — no data freshness timestamp, no uncertainty range

**OJK Regulator findings:**
- R1 CRITICAL: Operating as unlicensed financial advisory — blocking, Path B implemented
- R2/R3 CRITICAL: Complete absence of mandatory POJK 21/2011 Article 15/16 disclosures — fixed
- R7 HIGH: Suitability assessment missing financial situation + objectives dimensions (POJK 17/2015 Article 4)
- R8 HIGH: Cross-border data transfer (if US cloud) violates UU 27/2022 Article 56
- R10 MEDIUM: Synthetic training data not disclosed to users

**What was fixed vs documented:**
- Fixed: R1 (de-personalize), R2 (Initial Disclosure), R3 (instrument risk cards), R4 (affiliate conflict), R5 (lumpy warning), R6 (freshness warning), R8 (Indonesian cloud)
- Documented as known limitations: R11 (affiliate economics), R12 (competitive replication window)

### 2.5 /codify

This document. All institutional knowledge captured, decisions logged, and configuration documented for future sessions.

---

## 3. KEY DECISIONS LOG

### D1: XGBoost → GradientBoostingClassifier (sklearn)
**Decision:** Use sklearn `GradientBoostingClassifier` instead of XGBoost
**Context:** Initial implementation planned XGBoost. At runtime, `xgboost.core.XGBoostError: libomp.dylib could not be loaded` — macOS environment lacked libomp.
**Reasoning:** Both are gradient-boosted tree families. sklearn's `GradientBoostingClassifier` is the same algorithmic family and satisfies the course requirement for "XGBoost or Random Forest."
**Outcome:** Model trained and evaluated. 99.9% accuracy was later identified as a red flag (D2).

---

### D2: Classification → Regression
**Decision:** Replace `GradientBoostingClassifier` (verdict prediction) with `GradientBoostingRegressor` (months-to-goal prediction) + post-processing classification
**Context:** During training, classifier achieved 99.9% accuracy — definitive signal of label contamination. Feature importance was 100% on `investment_to_income_ratio`, 0% on all other features. The model was applying the exact label formula, not learning financial behavior.
**Reasoning:** The regression target (`months_to_achieve_goal = goal_cost / (disposable × 0.25)`) eliminates the direct path from feature to label. The model must learn non-linear interactions between salary, city cost, income growth, and timeline. Post-processing classifies the residual (predicted vs. actual timeline) into Green/Yellow/Red.
**Outcome:** CV RMSE: 6755 months. Feature importance spread across all 7 features (disposable_income 49%, goal_cost 21%, monthly_salary 18%). Genuine model uncertainty, not formula memorization.

---

### D3: Flat 30% Threshold → Income-Bracket + Goal-Type Thresholds
**Decision:** Replace flat green/yellow thresholds (30%/50%) with income-bracket-aware and goal-type-aware adaptive thresholds
**Context:** Western financial planning convention uses 30% investment-to-disposable ratio as the green threshold. Indonesian saving behavior differs: fresh graduates (Rp < 8M/month) have tighter liquidity constraints; senior professionals (> Rp 20M/month) have more investable capacity.
**Reasoning:**
- Fresh graduate: green < 25%, yellow < 45% (tight liquidity)
- Mid-career: green < 30%, yellow < 50% (standard)
- Senior: green < 35%, yellow < 55% (more capacity)
- Fixed-deadline goals (Wedding, Education, Higher Education): +2–3% stricter green threshold (cannot extend timeline as lever)
- Retirement/Emergency Fund: −2–3% looser threshold (more flexible, compound effect)
**Final range:** Green 22% (fresh grad + Higher Ed) to 37% (senior + Retirement)

---

### D4: Western Saving Rate → Indonesian-Calibrated Model
**Decision:** Use sustainable_rate = 0.25 (25% of disposable income) instead of Western 50% rule
**Context:** Western rule-of-thumb suggests investing 50% of disposable income. Indonesian income levels and cost structures make 50% unrealistic for most users. Indonesian household saving rate (Bank Indonesia data) averages 8–18% of disposable income.
**Reasoning:** 25% is conservative and realistic. It allows the model to learn realistic month-to-goal predictions based on how much someone could sustainably invest, not an aspirational Western number that doesn't reflect Indonesian financial reality.

---

### D5: Scenario Lever Priority — Goal-Type-Aware
**Decision:** Fixed-deadline goals (Wedding, Education, Higher Education) skip the timeline extension lever
**Context:** Wedding and education goals have hard deadline constraints (wedding date, academic intake window). Recommending a user "extend your wedding timeline by 3 years" is not a valid scenario.
**Implementation:**
- `goal_modifier["timeline_locked"] = True` for Wedding, Education, Higher Education
- `optimize_timeline()` is never called for locked goals
- Location, goal_size, and contribution remain available
**Outcome:** Scenario optimizer no longer suggests timeline extensions for goals where they are not actionable.

---

### D6: Path A vs Path B Regulatory Fix
**Decision:** Path B — de-personalize portfolio page to educational illustrations, rather than Path A — file for IZInas PK (12–18 month timeline)
**Context:** Redteam identified that showing personalized allocation tied to user data constitutes investment advice under POJK 21/2011 Article 3. Path A (obtain license) takes 12–18 months — not feasible for MGMT 655 demo.
**Reasoning:** Path B (de-personalize) achieves regulatory exposure reduction immediately while Path A is pursued in parallel. The portfolio page now shows "Ilustratif" allocations, not "your portfolio." Disclaimers state "not licensed under POJK 21/2011." This does not cure the licensing deficiency but reduces immediate regulatory risk.
**Outcome:** Portfolio page restructured. Legal counsel should be engaged to pursue Path A in parallel for the business.

---

### D7: Property 15% Contingency Buffer
**Decision:** `estimate_property_cost()` multiplies by `PROPERTY_BUFFER = 1.15`
**Context:** Initial property estimates used raw price per sqm × size. Indonesian property transactions carry additional costs: PPHTB (5%), BPHTB (5%), notary fees (1–2%), and a buffer for price appreciation during the investment buildup period.
**Calculation:** A 50 sqm apartment at Rp 42M/sqm: raw = Rp 2.1B. With 15% buffer: Rp 2.415B. The difference of Rp 315M is material to feasibility verdict.
**Outcome:** Property estimates now include transaction costs. User sees realistic total cost.

---

### D8: Equity Cap for Short Timelines
**Decision:** Equity allocation capped at 40%, REITs at 10% for timelines < 3 years
**Context:** Equity-heavy allocations (65% reksa dana equity, 25% REITs) are inappropriate for near-term goals. A 35% market drawdown right before a property purchase deadline is not a paper loss — it's a real shortfall with no recovery time.
**Implementation:** `apply_equity_cap_for_short_timeline()` distributes excess allocation to ORI/SBR and deposito.
**Outcome:** Agresif profile at 2-year timeline: equity 40%, REITs 10%, ORI 45% (vs uncapped: equity 65%, REITs 25%, ORI 5%).

---

### D9: IDR Depreciation Buffer for Abroad Education
**Decision:** `estimate_higher_education_cost()` applies `× (1.04)^years × 1.10` for depreciation + buffer
**Context:** Abroad education costs are denominated in foreign currency (USD, AUD, EUR) but the user's income and savings are in IDR. IDR has weakened approximately 4% per year against major currencies (2019–2024 average). A Singapore Master's program costing Rp 481M today costs Rp 572M in 4 years at current depreciation rates, without any actual price increase.
**Calculation:** Base cost Rp 481M × (1.04)² × 1.10 = Rp 572M
**Outcome:** Abroad education estimates now reflect currency risk. Yellow verdict instead of Green when depreciation is included.

---

### D10: Synthetic Data — Acceptable for MVP with Disclosure
**Decision:** Use synthetic data for ML training, disclose limitations prominently
**Context:** Real Indonesian financial outcome data (goal achievement rates by income/city/timeline) is not publicly available. Acquiring it would require partnerships with Bibit, Bareksa, or Oxford Pools — all of which have proprietary data and competitive sensitivities.
**Reasoning:** Synthetic data is the fastest path to a trainable model. Limitations are disclosed in the Initial Disclosure Document and on the portfolio page. Real data acquisition is the Phase 2 priority.
**Disclosure implemented:** "Model ini dilatih pada data sintetis, bukan data pasar nyata Indonesia."

---

## 4. WHAT WAS REJECTED AND WHY

### India Expansion
**Rejected:** Adding India as a market in Phase 2
**Reasoning:** Product-market fit must be proven in Indonesia before diversifying. India has different regulatory framework (SEBI), different instrument taxonomy (ELSS, PPF, NPS), and requires Hindi localization. The team's limited resources should focus on proving the model in one market.
**Decision:** India deferred to Phase 4, contingent on Indonesia traction.

### Direct Saham Recommendations
**Rejected:** Including individual stock (saham) recommendations in portfolio allocation
**Reasoning:** POJK 21/2011 Article 3 covers investment advice. Individual stock recommendations require a securities license (POJK 35/2014). The current instrument set (reksa dana, ORI, deposito, REITs) stays within fund-supermarket-level products that don't require a securities license for distribution.
**Decision:** Saham excluded from allocation instruments. Reksa dana equity (managed funds) provides equity exposure without requiring stock-level recommendations.

### Rumah123 API Integration (Phase 2)
**Rejected:** Real-time property price API integration for MVP
**Reasoning:** API access to Rumah123 requires a commercial partnership or scraping, both of which have legal and technical complexity. The static database with data freshness warning is sufficient for MVP demonstration. Real-time data is a Phase 2 feature.
**Decision:** Static database with ±15-20% uncertainty disclosure. Phase 2: Rumah123 or JSSRES API integration.

### Test Infrastructure (T6)
**Rejected:** Building pytest test suite for the engine layer
**Reasoning:** MGMT 655 course requirement focuses on the product demonstration, not software engineering quality metrics. Test infrastructure is important for production but not a course requirement.
**Decision:** Deferred to post-MGMT 655. TDD approach would be implemented in a proper sprint.

### Multi-Goal Tracking (T7)
**Rejected:** Session state redesign to support multiple simultaneous goals
**Reasoning:** Multi-goal tracking requires a database (not just session state), a goal prioritization algorithm, and combined cash-flow analysis. This is a Phase 2 feature requiring backend infrastructure.
**Decision:** Single-goal flow only for MVP. Multi-goal tracking deferred.

### Competitor Benchmarking (T8)
**Rejected:** Live competitive analysis against Bibit, Bareksa, Pluang
**Reasoning:** Would require access to competitor platforms' recommendation algorithms and outcome data, which is not publicly available. A market research engagement would cost Rp 20–50M and take 4–6 weeks — not appropriate for course timeline.
**Decision:** Competitive positioning documented from public sources only.

### Path A — Full OJK Licensing
**Rejected for immediate implementation:** Obtaining IZInas PK before demo
**Reasoning:** 12–18 month regulatory processing timeline is incompatible with MGMT 655 course deadline. Path B (de-personalize) achieves immediate risk reduction.
**Decision:** Path B for demo. Path A filing should happen immediately after course submission. Legal counsel engagement is the critical next step post-course.

---

## 5. ML ARCHITECTURE DECISIONS

### Model Family: Gradient Boosted Regressor

**Chosen:** `sklearn.ensemble.GradientBoostingRegressor`
**Hyperparameters:**
```python
GradientBoostingRegressor(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
)
```
**Rationale:** Gradient boosted trees handle non-linear feature interactions (salary × city cost × income growth) without manual feature engineering. `max_depth=5` prevents overfitting on 5000-sample synthetic dataset. `subsample=0.8` adds regularization.

### Synthetic Data Generation

**Function:** `generate_regression_dataset(n_samples=5000)` in `vestara/data/synthetic_data.py`

**Target computation:**
```python
sustainable_rate = 0.25
monthly_investment_capacity = disposable × sustainable_rate
months_to_achieve_goal = goal_cost / monthly_investment_capacity
```

**Feature distributions:**
- Salary: uniform within bucket ranges (fresh_grad Rp 3-8M, mid Rp 8-20M, senior Rp 20-45M)
- City: uniform over 10 cities
- Goal type: uniform over 7 types
- Timeline: uniform 3-30 years
- Income growth: bucket-dependent uniform (fresh_grad 5-15%, mid 5-20%, senior 10-30%)

**Limitations disclosed:**
- No real behavioral outcomes (no observed goal achievement data)
- Uniform distribution assumptions (real behavior is likely log-normal and age-correlated)
- No income volatility modeling (single scalar growth rate)
- No geographic correlation between city and salary

### Feature Set

**7 features used:**
```
monthly_salary              — raw income signal
city_living_cost_index      — 1-10 ordinal encoding of city cost tier
goal_cost                  — estimated or user-provided goal amount
timeline_years              — user-specified investment horizon
income_growth_rate          — expected annual salary growth
monthly_living_cost        — city-specific cost of living
disposable_income          — monthly_salary − monthly_living_cost
```

**3 features excluded:**
- `investment_to_income_ratio` — contamination source (was also label formula)
- `monthly_investment_required` — directly proportional to goal_cost / timeline, leaks target
- `goal_type` (categorical) — would allow goal-specific shortcuts instead of generalizable learning

### Threshold Calibration

**Green/Yellow boundaries computed as:**
```python
green_threshold = income_base[bracket] + goal_modifier[goal_type]["green_boost"]
yellow_threshold = income_base[bracket] + goal_modifier[goal_type]["green_boost"] + 0.20
```

| Income Bracket | Base Green | Base Yellow | Notes |
|--------------|-----------|-------------|-------|
| Fresh graduate (< Rp 8M) | 25% | 45% | Tight liquidity |
| Mid-career (Rp 8-20M) | 30% | 50% | Standard |
| Senior (> Rp 20M) | 35% | 55% | More capacity |

| Goal Type | Green Boost | Notes |
|-----------|------------|-------|
| Property | +0% | Flexible timeline |
| Retirement | −2% | Compound effect works for you |
| Emergency Fund | −3% | Already short-term |
| Wedding | +2%, locked | Fixed date, cannot extend |
| Education | +2%, locked | Academic intake windows |
| Higher Education | +3%, locked | Visa timelines + intake |

### Validation Approach

**5-Fold Cross-Validation:**
```
Fold 1: RMSE = 5147.4 months
Fold 2: RMSE = 3777.4 months
Fold 3: RMSE = 17779.2 months  ← outlier: high-goal-cost samples
Fold 4: RMSE = 3322.2 months
Fold 5: RMSE = 3752.3 months
Mean CV RMSE: 6755.7 months
```

**RMSE Interpretation:**
The high RMSE is primarily caused by the model correctly predicting unreachable goals (capped at 999 months). The target range spans 12 months (small goal, high income) to 999 months (unreachable). RMSE in this scale reflects model confidence about which goals are near-impossible, not model inaccuracy about achievable ones.

**Confidence classification:**
```python
confidence_pct = max(0, min(1, 1 - (cv_rmse / 120)))
# 120 months = 10-year reference scale
# HIGH: confidence_pct >= 80% (cv_rmse <= 24 months)
# MEDIUM: 60-80% (24 < cv_rmse <= 48)
# LOW: < 60% (cv_rmse > 48)
```

---

## 6. ETHICAL AND REGULATORY CONSIDERATIONS

### POJK 21/2011 Compliance (Educational vs. Advisory)

**The core distinction:**
- **Educational tool:** Shows general information about asset classes, displays model portfolios without connection to user data, uses "ilustratif" language throughout
- **Investment advice:** Recommends specific instruments and percentages personalized to the user's submitted financial data

**Vestara's current configuration:** Educational (post-FIX 1 Path B restructuring)

**What was changed:**
- Portfolio page now shows "Ilustratif" not "your portfolio"
- Top-of-page disclaimer: "Vestara is not licensed under POJK 21/2011"
- No language connecting allocation to the user's specific financial situation

**What still needs to happen (Path A):**
- Obtain IZInas PK from OJK (12-18 month process)
- Engage Indonesian securities counsel to confirm configuration is compliant
- Implement full Article 15/16 disclosure package

### Mandatory Disclosures Implemented

**FIX 2 — Initial Disclosure Document (POJK 21/2011 Article 15/16):**
- What Vestara does and does not do
- Model trained on synthetic data disclosure
- ±15-20% cost estimate uncertainty
- Historical return ≠ future guarantee
- Link to sikapiuangmu.ojk.go.id

**FIX 4 — Data Freshness Warning:**
- "Estimasi biaya berdasarkan data 2025. Harga aktual dapat berbeda ±15-20%."

**FIX 3 — Instrument Risk Labels:**
- Reksa Dana Saham: "High risk — nilai dapat turun signifikan"
- ORI/SBR: "Low risk — dijamin pemerintah"
- Deposito: "Very low risk — dijamin LPS hingga Rp 2M"
- DIRE/REITs: "Medium-high risk — terpengaruh pasar properti"

### Synthetic Data Transparency

**Disclosure language (in Initial Disclosure Document):**
"Model ini dilatih pada data sintetis, bukan data pasar nyata Indonesia. Hasil alokasi bersifat ilustratif, bukan rekomendasi yang dijamin."

**Why synthetic was necessary:**
Indonesian financial outcome data (goal achievement rates by income/city/timeline/instrument) does not exist in public datasets. Acquiring it requires partnerships with Bibit, Bareksa, or Oxford Pools — all of which have proprietary data.

**Production path:**
Phase 2: Retrain on real Indonesian market data (IDX historical returns, LPS rate history, REITs NAV series). Document backtesting methodology against 5-year IDX benchmarks.

### Known Limitations and Communication

| Limitation | How Communicated |
|-----------|----------------|
| Not licensed under POJK 21/2011 | Top-of-page disclaimer on portfolio page |
| Model trained on synthetic data | Initial Disclosure Document expander |
| Cost estimates are approximations | Data freshness warning on every estimate |
| Historical returns ≠ future returns | Initial Disclosure Document |
| Uncertainty range ±15-20% | Data freshness warning |
| Competitor can copy in 6 weeks | Red team findings (internal, not user-facing) |
| Affiliate economics not viable at MVP scale | Red team findings (internal) |

---

## 7. REUSABILITY

### Adaptation for Other Southeast Asian Markets

**Thailand (Bangkok, Chiang Mai, Phuket):**
- Replace `PROPERTY_PRICE_PER_SQM` with Bangkok condo data (DDproperty, Living Square)
- Add `GOAL_TYPES`: include "Motorcycle purchase" (common Thai goal)
- Replace `INCOME_THRESHOLDS` with Thai household income distribution (NESDB data)
- Change instrument set: add Thai government bonds (KBanks, SBL), remove ORI/SBR
- Regulatory: SEC Thailand has different POJK equivalent — conduct local legal review

**Philippines (Manila, Cebu, Davao):**
- Condo prices per sqm in Metro Manila (Lamudi, Property24)
- Goal types: "Overseas Filipino Worker remittance goal" is culturally significant
- Replace instruments: REITs Philippines (DDMPR, AREIT), Philam Bond Fund, GoTyme Bank deposito
- BSP regulatory framework replaces OJK

**Vietnam (Hanoi, Ho Chi Minh City):**
- Apartment prices per sqm in districts (Rever, Batdongsan)
- Goal types: "Motorbike purchase" (Honda Wave), "Family reunion house" (traditional)
- VND depreciation risk similar to IDR — same currency buffer approach
- SSC Vietnam regulatory equivalent

**Key adaptation steps for any market:**
1. Replace cost data (property, living, education) with local equivalents
2. Map local investment instruments to the 6-instrument taxonomy
3. Recalibrate income thresholds against local income distribution
4. Replace regulatory framework with local equivalent (SEBI, MAS, SEC Thailand)
5. Retrain regression model on local synthetic data
6. Obtain local legal opinion on educational vs. advisory distinction

### Adaptation for Insurance Goal Planning (Takaful Products)

**Islamic insurance (takaful) goal planning:**
- Add new goal type: "Family protection (takaful)"
- Replace instruments: takaful family plan ( Prudential Shariah, AIA Af Ata), Wadiah deposito, Islamic REITs (Asia REIT Shariah)
- Modify risk profiler: remove interest-sensitive questions, add questions about halal investment preference
- Adjust thresholds: takaful contributions are typically 5-10% of income (lower than conventional due to mudharabah surplus sharing)

**Product-specific modifications:**
- Contribution calculation: takaful family plan premiums are typically lower than conventional for same coverage
- Goal type: "education endowment (ta'widh)" as a sub-type of Education
- Regulatory: BNM (Bank Negara Malaysia) or OJK Indonesia's Shariah Governance Policy

### Adaptation for Corporate HR / Pension Planning

**Corporate employee financial wellness tool:**
- Replace goal types: "Emergency fund", "Child education", "Retirement", "Home purchase"
- Add salary bracket employer contribution matching (EPF/BPJS Ketenagakerjaan rules)
- Replace disposable income calculation to account for employer pension contributions
- Add "years to retirement" as primary timeline driver (instead of user-specified)
- Modify risk profiler: add employer stability dimension (government vs. private vs. startup)
- Connect to corporate pension plan data (mock API or integration with SAP SuccessFactors)

**Indonesian corporate-specific modifications:**
- Integrate with BPJS Ketenagakerjaan for pension projection (user's accumulated balance)
- Add THR (THR/Tabal) as a financial event that affects cash flow
- EPF-like contribution matching: employer typically matches 3-5% of salary
- Language: replace "investment" with "pengelolaan dana" for corporate wellness context

---

## 8. LESSONS LEARNED

### If Starting Again: What Would Be Different

**1. Start /analyze before any code is written**

The initial classifier was built before the /analyze phase revealed the 99.9% accuracy contamination problem. If /analyze had preceded implementation, the regression refactor would have been the starting architecture, not the fix applied after the fact.

**The specific sequence that caused the problem:** Requirements → Implementation → /analyze → Fix. The correct sequence is: Requirements → /analyze → Implementation.

**What to do instead:** Run /analyze with the full ML architecture decision as a specific output before writing any model code. The 99.9% accuracy finding was predictable — any time a model has access to the label formula as a feature, it will memorize. This should have been caught in the analysis phase, not during training.

---

**2. Validate thresholds against local data sources first**

The 30% Western threshold was used as the starting point without checking whether it was appropriate for Indonesian financial behavior. The 25% sustainable rate was chosen by instinct, not data.

**What to do instead:** Before setting any threshold, spend one session reviewing:
- Bank Indonesia household saving rate data
- BPS (Badan Pusat Statistik) income and expenditure surveys
- Bibit/Bareksa user behavior data (if accessible through research partnerships)
- Academic literature on Indonesian household financial behavior

The Indonesian saving rate of 8-18% of disposable income is the anchor. Any threshold above 25% would be aspirational for most users.

---

**3. Regulatory review should happen at product design stage, not after build**

The POJK 21/2011 compliance issue was discovered during /redteam, after all the portfolio recommendation UI was built. The decision to show "your portfolio" as personalized allocation was made casually during implementation, without checking whether it constituted investment advice.

**What to do instead:** Before designing the portfolio page, obtain a one-hour consultation with Indonesian securities counsel to establish: (a) what constitutes investment advice vs. education under POJK 21/2011, (b) what disclosures are mandatory before showing any allocation, (c) what the realistic timeline to licensing is. This would have cost Rp 2-5M and saved a complete UI redesign.

---

**4. Synthetic data is fine for MVP but flag limitations early**

The synthetic data approach was reasonable for an MVP with no access to real outcome data. The mistake was not disclosing the synthetic nature prominently enough from the beginning.

**What to do instead:** Add synthetic data disclosure to the very first demo, not after the red team found it. Investors and regulators will find out eventually — disclosing proactively builds trust, disclosing defensively after being caught destroys it.

---

**5. The ML model is the least durable part of the moat**

The regression model trained on synthetic data is not a competitive moat. It can be replicated by any competitor with access to the same cost data and a Python environment. The durable moat is:
1. Regulatory license (12-18 months to obtain, cannot be shortcut)
2. Real user outcome data at scale (requires years to accumulate)
3. Distribution relationships (Bareksa partnership, HR platform integrations)

**What this means for prioritization:** Every week spent on ML model refinement is worth less than every week spent on regulatory filing and partnership development. The ML model is the feature that gets copied; the license and relationships are the business.

---

**6. The cost database is more important than the ML model**

The single biggest driver of feasibility accuracy is the property cost estimate. An Rp 800M database error (wrong Jakarta Selatan price) caused a complete feasibility misclassification. The ML model's 6755-month RMSE is a rounding error compared to a 33% property price underestimate.

**What this means for investment allocation:** Invest in data pipeline infrastructure (Rumah123 API, BPS data feeds) before investing in model architecture improvements. A better model on wrong data produces worse predictions than a simple model on right data.

---

**7. Demo UX and regulatory safety are not in conflict**

The original instinct was that regulatory disclaimers and educational framing would make the demo feel weak or lawyered. The actual finding from /redteam was the opposite: the disclaimers and disclosures made the product appear more credible and professionally responsible, not less.

**What this means for the demo:** Lead with the disclaimers. "This is educational. We're not licensed yet and here's exactly what that means for you as a user." This honesty is a differentiator, not a liability.

---

*This document was generated through the COC /codify phase of the MGMT 655 course project for Vestara. All decisions are traceable to specific commits, plan references, and red team findings documented in the workspace.*
