# Vestara — Financial Goal Planning Platform

**Status**: Functional prototype — all 5 pages operational
**Stack**: Python · Streamlit · scikit-learn · Indonesian cost data (2025)
**Audience**: Business manager · End user · Developer taking over

---

## What Is Vestara?

Vestara is a goal-first investment planning platform for Indonesian users. It guides a user through a 4-step workflow:

1. **Define a life goal** (property, retirement, education, wedding, emergency fund) with cost projected to the target year using Indonesian inflation data
2. **Analyze feasibility** — can they afford it given their income, expenses, and timeline?
3. **Assess their risk profile** — Konservatif (conservative), Moderat (moderate), or Agresif (aggressive)
4. **Generate an optimised portfolio allocation** across Indonesian investment instruments

The app is a Streamlit web application with a premium glassmorphism UI (navy/violet/cyan theme). It requires no external API keys — all data is public scraping, BPS anchor data, or hardcoded 2025 baseline figures.

---

## Business Manager: Why This App Is Ready to Launch

### What Ships at Launch

**Scope: Jakarta-only, 5 active goal types**

| Goal             | Status                                                       |
| ---------------- | ------------------------------------------------------------ |
| Property         | Active — Apartment and Landed House, 5 Jakarta areas         |
| Retirement       | Active — 3 lifestyle tiers                                   |
| Emergency Fund   | Active — 3 coverage durations                                |
| Education        | Active — Government through International schools            |
| Higher Education | Active — Indonesia + 7 abroad countries                      |
| Wedding          | Active — Full scale/venue/catering/entertainment multipliers |
| Custom           | Active — User-supplied goal amount                           |

Coming soon: Bandung, Surabaya, Yogyakarta (city expansion is a data entry task, not a code task).

### The Numbers Are Real

Property price baselines use **Colliers International Q1 2025** figures — Jakarta Selatan at Rp 35M/sqm, Jakarta Pusat at Rp 23M/sqm, down to Jakarta Timur at Rp 18M/sqm. School fees, higher education tuition, wedding costs, and retirement living expenses are all anchored to 2025 Indonesian figures with documented inflation rates (6% property, 8–12% education, 4% retirement, 5% wedding). A 15% buffer is applied to all property transactions to cover PPHTB, BPHTB, notary, and agent fees.

### Three ML-Powered Insights No Spreadsheet Gives You

**1. Feasibility score that accounts for your whole financial picture**
The app collects monthly salary, city of residence, existing investments, and goal cost, then trains a GradientBoostingRegressor on synthetically-generated financial trajectories to predict how many months the goal realistically takes. This is not a formula — it is a model that has learned how disposable income, timeline, income growth, and cost inflation interact across thousands of simulated scenarios.

**2. Peer benchmarking via KMeans clustering**
The app clusters the user against 4 financial archetypes (Sultan, Survivors, Professionals, Petugas) using income bracket, savings rate, and investment experience. The user sees which archetype they match and how many peers they have in the same segment — a social proof signal that makes the output more credible than a generic score.

**3. Risk-aware portfolio allocation**
The portfolio optimizer maps the user's risk profile (derived from 12 questions across 8 financial dimensions) to a fixed allocation across 6 Indonesian instruments: deposito, obligasiORI/SBR, reksa dana pasar uang, reksa dana pendapatan tetap, reksa dana saham, and REITs. For timelines under 3 years, equity and REITs are automatically capped at 40% and 10% respectively to prevent short-term drawdown risk.

### No API Keys, No Vendor Lock-In

All data pipelines are either public scraping (Numbeo), static BPS anchor data, or hardcoded seed values. The app runs entirely locally or on any Streamlit-compatible hosting (Streamlit Cloud, HuggingFace Spaces, a VPS). The only Python dependency beyond Streamlit is scikit-learn — a mature, well-maintained library with no commercial licensing concerns.

### What a 2-Hour Launch Requires

1. Deploy with `streamlit run` — no Docker, no Kubernetes
2. Load the Colliers Q1 2025 price data into `vestara/data/cache/rumah123_prices.json`
3. Set `DEBUG=False` in `.env` to disable any development-only paths

---

## End User: What the App Does When You Use It

### The 4-Step Wizard

**Step 1 — Define Your Goal**

Choose a goal type and answer a short series of questions. For a property goal, you select the property type (apartment or landed house), the area within Jakarta (Jakarta Selatan, Jakarta Pusat, Jakarta Utara, Jakarta Timur, or Jakarta Barat), the unit size, and your target purchase year. For retirement, you enter your current age, retirement age, desired city and area, monthly lifestyle spend, and life expectancy. The app projects every cost to the target year using Indonesian inflation rates.

**Step 2 — Check Feasibility**

Enter your monthly income and expenses. The app calculates your disposable income (income minus expenses) and runs it through a machine learning model trained on thousands of simulated financial trajectories. It returns:

- A **feasibility score** (0–100)
- A **verdict** — Green ("You are on track"), Yellow ("Achievable with adjustments"), Red ("Significant gap")
- A **confidence level** — HIGH/MEDIUM/LOW based on how similar your financial profile is to the training data
- Your **peer archetype** — how you compare to other users in the same income and experience bracket

**Step 3 — Risk Profile**

Answer 12 questions about how you invest, how you react to losses, how stable your income is, and what your financial obligations look like. The app maps your total score to one of three profiles:

- **Konservatif** (score 12–30) — prioritises capital preservation
- **Moderat** (score 31–45) — balanced growth and safety
- **Agresif** (score 46–60) — long-term growth orientation

**Step 4 — Your Portfolio**

The app generates a projected portfolio value at your goal year, a blended annual return rate, and a shortfall or surplus versus your target. It shows a breakdown of how your monthly contribution would be allocated across 6 Indonesian investment instruments, and a growth trajectory chart showing how the portfolio compounds over your timeline.

### How the App Handles Indonesian-Specific Costs

Property costs include a 15% transaction buffer (PPHTB, notary, agent fees). School fees use 2025 figures by school type — government schools at Rp 2.5–3M/year, international schools at Rp 140–180M/year. Higher education abroad includes a 10% currency risk buffer on top of tuition and living cost projections. Retirement costs project monthly spend to the retirement year using a 4% annual inflation rate.

### What the App Does Not Do

The app does not connect to your bank account, brokerage, or pension fund. It does not execute trades. It is a planning and projection tool — the output is an informational guide, not financial advice. All projections are based on stated assumptions (income, expenses, timeline) and publicly available cost data.

---

## Developer Taking Over: Architecture and Key Implementation Details

### Project Structure

```
vestara/
├── src/
│   ├── ui/
│   │   └── app.py                  # 2,240-line Streamlit app
│   ├── engine/
│   │   ├── goal_builder.py         # Goal cost calculators
│   │   ├── risk_profiler.py        # Risk questionnaire + profiler
│   │   ├── feasibility_regression.py  # GradientBoostingRegressor
│   │   ├── feasibility_classifier.py  # Older classifier (superseded)
│   │   ├── peer_clustering.py      # KMeans k=4 clustering
│   │   └── scenario_optimizer.py   # 4-lever what-if analysis
│   └── portfolio/
│       └── optimizer.py            # PortfolioProjection builder
├── data/
│   ├── cost_data.py               # All Indonesian cost seed data
│   ├── fetcher.py                 # Numbeo scraper + regression model
│   └── synthetic_data.py          # Training data generators
└── models/                        # Saved ML model files (pickle)
```

### Tech Stack

- **Streamlit** — web UI framework
- **scikit-learn** — GradientBoostingRegressor, KMeans, train_test_split
- **numpy, pandas** — data processing
- **No external API keys** — all data is public scraping or static seed

### Key Data Structures

**`GoalProfile`** (goal_builder.py):

```python
goal_type: str          # "Property", "Education", etc.
city: str              # "Jakarta", "Bandung", etc.
area: str              # "Jakarta Selatan", etc.
estimated_cost: float  # inflation-projected to target year
timeline_years: int   # years until target
description: str       # human-readable summary
```

**`RiskProfile`** (risk_profiler.py):

```python
profile: str   # "Konservatif", "Moderat", "Agresif"
score: int     # 12-60
```

**`PortfolioProjection`** (portfolio/optimizer.py):

```python
allocations: list[PortfolioAllocation]   # instrument, percentage, monthly_amount, expected_return
blended_return: float
blended_volatility: float
projected_value_at_goal_year: float
goal_amount: float
timeline_years: int
yearly_trajectory: list[tuple[int, float]]
```

**`PortfolioAllocation`**:

```python
instrument: str       # e.g. "reksa_dana_equity"
percentage: float     # e.g. 22.0
monthly_amount: float
expected_return: float
expected_growth_10yr: float
```

### Session State Keys

| Key                     | Type                 | Purpose                          |
| ----------------------- | -------------------- | -------------------------------- |
| `page`                  | str                  | Current page name                |
| `goal_step`             | int                  | Wizard step index (0-indexed)    |
| `goal_step_answers`     | dict                 | All answers collected so far     |
| `goal_profile`          | dict                 | GoalProfile as dict              |
| `goal_set`              | bool                 | Goal calculation complete        |
| `risk_profile`          | dict                 | `{"profile": str, "score": int}` |
| `risk_profile_set`      | bool                 | Risk profiling complete          |
| `feasibility_result`    | dict                 | Score, verdict, confidence       |
| `portfolio_result`      | PortfolioProjection  | From build_portfolio()           |
| `feasibility_regressor` | FeasibilityRegressor | Trained model instance           |

### How the Feasibility ML Works

The older `feasibility_classifier.py` used a GradientBoostingClassifier that achieved 99.9% training accuracy by memorizing the `investment_to_income_ratio` formula rather than learning financial behaviour — it was abandoned.

The current `feasibility_regression.py` uses a **GradientBoostingRegressor** (n_estimators=200, max_depth=5, learning_rate=0.1, subsample=0.8). Training data is synthetically generated via `generate_regression_dataset()` in `synthetic_data.py`, where the target is `months_to_achieve_goal = goal_cost / (disposable_income × 0.25)` — simulating a user who invests 25% of their disposable income monthly. The 7 features are: `monthly_salary`, `city_living_cost_index`, `goal_cost`, `timeline_years`, `income_growth_rate`, `monthly_living_cost`, `disposable_income`.

Post-processing converts the predicted month count into a verdict:

- **Green**: predicted months < 85% of stated timeline
- **Yellow**: 85–115% of timeline
- **Red**: >115% of timeline

Confidence is HIGH if 5-fold CV RMSE is below 20% relative error, MEDIUM if 20–40%, LOW if above 40%.

### How the Risk Profiler Works

12 questions, each scored 1–5, covering: investment horizon, loss tolerance, income stability, financial obligations, debt burden, investment experience, volatility tolerance, liquidity need, emergency fund status, goal urgency, financial knowledge, discipline. Total score max is 60. Profile bands are fixed: 12–30 = Konservatif, 31–45 = Moderat, 46–60 = Agresif.

### How the Portfolio Optimizer Works

`build_portfolio()` in `portfolio/optimizer.py` takes `risk_profile`, `monthly_contribution`, `goal_amount`, `timeline_years` and returns a `PortfolioProjection`. Allocation is rule-based (not Markowitz optimisation):

| Instrument                  | Konservatif | Moderat | Agresif |
| --------------------------- | ----------- | ------- | ------- |
| Deposito                    | 30%         | 15%     | 0%      |
| ObligasiORI/SBR             | 40%         | 25%     | 5%      |
| Reksa Dana Pasar Uang       | 15%         | 10%     | 0%      |
| Reksa Dana Pendapatan Tetap | 10%         | 20%     | 5%      |
| Reksa Dana Saham            | 5%          | 22%     | 65%     |
| REITs                       | 0%          | 8%      | 25%     |

For timelines under 3 years, equity is hard-capped at 40% and REITs at 10% regardless of risk profile.

### The Area Model (Fetcher)

When property price data for an unknown area is requested, `fetcher.py` trains an OLS linear regression model with ridge regularisation on 15 pre-collected area samples (features: distance to CBD, business district count, toll access score, mall count, population density). This produces a `PricePoint(price_per_sqm, source="AreaModel", reliability="MEDIUM")` for areas not in the Colliers baseline.

### CSS Theme

The app uses a custom CSS theme defined in `app.py` (injected via `st.markdown` with `unsafe_allow_html=True`). Key variables:

```css
--bg-primary: #060912 --bg-card: rgba(17, 17, 35, 0.85) --violet-500: #8b5cf6
  --cyan-400: #22d3ee --glass-border: rgba(139, 92, 246, 0.2);
```

### Adding a New Goal Type

1. Add step definitions to `goal_builder.py` — define `STEPS` dict entry with step names and field keys
2. Add a `calculate_{goal_type}()` function in `goal_builder.py`
3. Add to `GOAL_TYPES` list in `cost_data.py`
4. Add the goal card in the Goals page switch statement in `app.py`
5. No ML retraining needed — the feasibility and portfolio engines are goal-agnostic

### Adding a New City

1. Add city to `ACTIVE_CITIES` or `COMING_SOON_CITIES` in `cost_data.py`
2. Add areas to `CITY_AREAS[city_name]`
3. Add baseline property prices to `BASELINE_FALLBACK_APARTMENT_PRICE_PER_SQM`
4. Add living costs to `BASELINE_FALLBACK_LIVING_COST_MONTHLY`
5. Add wedding costs to `WEDDING_BASE_COST`
6. No engine changes — all lookups are dict-based

### Running the App

```bash
cd vestara
PYTHONPATH=. streamlit run src/ui/app.py
```

Or with a specific port:

```bash
PYTHONPATH=. streamlit run src/ui/app.py --server.port 8501
```
