# 001 — Primary User Flow

## Overview

The user flow follows 5 stages across 5 pages in the Streamlit UI. Each stage is stateful — session state carries data forward. A user can exit and return; their progress is preserved.

**User persona:** Aditya, 27, software engineer at a Jakarta tech startup, Rp 12M/month take-home salary, no dependents, hoping to buy a 2BR apartment in Jakarta Selatan in 7 years.

---

## Stage 1: Onboarding

**Page:** Goal Builder (page 1 of 5)

**Inputs collected:**
- Name: "Aditya" (display only, not stored)
- City: "Jakarta Selatan" (dropdown, 10 cities)
- Monthly take-home salary: Rp 12,000,000 (number input)
- Expected annual income growth rate: 8% (slider, 0–30%)

**System behavior:**
- City determines `LIVING_COST_MONTHLY` lookup (Jakarta Selatan = Rp 8,500,000/month)
- Income growth rate stored as `income_growth` for use in feasibility computation
- All values stored in `st.session_state`

**What Aditya sees next:**
After entering city and salary, the page reveals goal-type selection.

---

## Stage 2: Goal Selection

**Page:** Goal Builder (continued)

### Step 2a: Choose Goal Type

**7 options presented as a selectbox:**
- Property (selected by most users)
- Education
- Retirement
- Emergency Fund
- Wedding
- Higher Education
- Custom

### Step 2b: Goal-Specific Follow-Up Questions

**If Property:**
1. Unit size: Studio/1BR (24–36 sqm) | 2BR Standard (45–54 sqm) | 2BR Large/3BR (70–90 sqm) | Large/Penthouse (90–150 sqm)
2. Neighborhood (optional text field): e.g., "Kemang", "Senayan"
3. Timeline: slider 1–40 years (default: 10)

**If Education (local):**
1. Level: TK/SD (Elementary) | SMP (Junior High) | SMA/SMK (Senior High)
2. School type: Local Private (J煲0–15M/yr) | Mid-tier Private (15–30M/yr) | Premium Private (30–60M/yr) | International School (60–150M/yr)
3. Timeline: same slider

**If Higher Education (abroad):**
1. Degree: Bachelor's | Master's | PhD/Doctorate
2. Country: Australia | Europe | Singapore | US | Other
3. Institution tier: Public/State University | Private University | Top 50 Global | Ivy League/Oxbridge
4. Timeline: default 4 years

**If Retirement:**
1. Current age: 18–65 (number input, default 25)
2. Retirement age: 45–75 (number input, default 55)
3. Lifestyle: Basic (2–3M/month) | Comfortable (4–6M/month) | Premium (7–10M/month)
4. Timeline: computed as retirement_age − current_age (not user-adjustable)

**If Wedding:**
1. Scale: Simple/Intimate (50–100 guests) | Moderate/Traditional (200–400 guests) | Grand/Bilingual (500+ guests)
2. Timeline: 1–10 years (fixed-deadline goal)

**If Emergency Fund:**
1. Coverage: 3 months (minimum) | 6 months (standard) | 12 months (conservative)
2. Timeline: 1–2 years maximum (not adjustable beyond this)

**If Custom:**
1. Choice: Enter a target amount directly | Describe goal and get estimate
2. Target amount: Rp number input (if first option selected)
3. Description: free text (if second option selected)
4. Timeline: 1–40 years

### Step 2c: Cost Estimation

When user clicks **"Estimate Goal Cost"**:

`GoalBuilder.build_goal()` is called, returning a `GoalProfile`:

```
goal_type: "Property"
city: "Jakarta Selatan"
estimated_cost: Rp 2,415,000,000  (50 sqm × 42M × 1.15 buffer)
timeline_years: 7
description: "2BR Standard (45-54 sqm) in Jakarta Selatan"
```

**What Aditya sees:**
- Large green success box: "Estimated Cost: Rp 2,415,000,000"
- Caption: "2BR Standard (45-54 sqm) in Jakarta Selatan | 7 years"
- Info box: "Proceed to Feasibility Analysis to check if this goal is achievable with your income"

**Session state updated:**
```python
st.session_state["goal_profile"] = profile.to_dict()
st.session_state["goal_set"] = True
```

---

## Stage 3: Feasibility Analysis

**Page:** Feasibility Analysis (page 2 of 5)

**Entry condition:** `goal_set` must be True, otherwise warning shown and `st.stop()`

### Step 3a: User Inputs

- Monthly take-home salary: pre-filled with value from Goal Builder, editable
- Expected annual income growth: pre-filled with value from Goal Builder, editable

**System displays (read-only):**
- Goal Amount: Rp 2,415,000,000
- Timeline: 7 years
- Goal Type: Property
- City: Jakarta Selatan

### Step 3b: Feasibility Computation

When user clicks **"Analyse Feasibility"**:

`compute_feasibility()` is called:
```
monthly_living = LIVING_COST_MONTHLY["Jakarta Selatan"] = 8,500,000
monthly_required = goal_cost / (timeline_years × 12)
                = 2,415,000,000 / 84
                = 28,750,000/month

disposable = monthly_salary − monthly_living
           = 12,000,000 − 8,500,000
           = 3,500,000

ratio = min(monthly_required / disposable, 2.0)
      = min(28,750,000 / 3,500,000, 2.0)
      = min(8.21, 2.0) = 2.0 (capped at 200%)
```

**Verdict: RED** (ratio 200% >> 50%)

### Step 3c: Verdict Display

**Three-column metric display:**
- Column 1: "Verdict" → "🔴 Red"
- Column 2: "Monthly Investment Needed" → "Rp 28,750,000"
- Column 3: "Investment-to-Salary Ratio" → "239.6%"

**Three-column breakdown:**
- Column 1: "Monthly Living Cost" → "Rp 8,500,000"
- Column 2: "Disposable Income" → "Rp 3,500,000"
- Column 3: "Required Monthly Investment" → "Rp 28,750,000"

### Step 3d: Scenario Analysis (only for Yellow/Red)

Below the breakdown, a gray info box explains:
> "Priority adjustments (easiest to hardest):
> 1. Extend timeline — giving your money more time to compound
> 2. Adjust location — choosing a lower-cost city or neighbourhood
> 3. Reduce goal size — a smaller target with the same timeline
> 4. Increase monthly contribution — investing more each month"

`run_scenario_analysis()` is called with:
```
goal_type = "Property"  (not locked, timeline is a valid lever)
income_bracket = "mid_career"  (12M salary)
green_threshold = 30%  (mid_career base, no goal-type modifier)
```

**Result:** RED with 3 scenarios:
1. **TIMELINE:** Extend from 7 to 24 years → monthly drops to Rp 8,375,000, ratio hits 29.6% → GREEN
2. **GOAL_SIZE:** Reduce goal by 78% → monthly drops to Rp 6,325,000, ratio hits 29.9% → GREEN
3. **LOCATION:** Move to Medan → living cost drops to Rp 3,500,000, disposable becomes Rp 8,500,000 → GREEN
4. Contribution lever is blocked because ratio > 100%

**What Aditya sees:**
Each scenario shown as expandable expander (first one expanded by default):
- "📌 TIMELINE: Extend from 7 to 24 years"
- "New investment ratio: 29.6% → Verdict: GREEN"
- Recommended scenario badge on first option

---

## Stage 4: Risk Profiling

**Page:** Risk Profiler (page 3 of 5)

**Entry condition:** Must complete Goal Builder and Feasibility Analysis first (not enforced, but recommended)

### The 12 Questions

Questions shown 3 at a time across 4 pages. Progress bar at top shows "Questions 1–3 of 12", "Questions 4–6 of 12", etc.

**Question topics and options (abbreviated):**

Q1. Loss tolerance: "I can accept a 20% portfolio drop without changing my strategy" — Strongly Agree / Agree / Neutral / Disagree
Q2. Income stability: "My job income is predictable month-to-month" — Very stable / Stable / Somewhat stable / Unstable
Q3. Debt load: "My monthly debt payments are..." — None / <10% of income / 10–30% / >30%
Q4. Dependents: "I have people depending on my income" — None / 1 person / 2–3 people / 4+
Q5. Investment knowledge: "I understand how investment instruments differ" — Expert / Good knowledge / Basic / None
Q6. Time horizon: "I am investing for..." — <3 years / 3–7 years / 8–15 years / 15+ years
Q7. Liquidity needs: "I may need to access my investments in..." — 1 year / 1–3 years / 3–5 years / 5+ years
Q8. Ethical preferences: "I prefer investments that align with ESG values" — Strongly prefer / Prefer / Neutral / No preference
Q9. Emergency fund: "I have emergency savings covering..." — 6+ months / 3–6 months / 1–3 months / None
Q10. Other investments: "I already have investments outside this goal" — Significant / Some / Small / None
Q11. Real estate plans: "I plan to buy property within 5 years" — Yes / Possibly / No / Already own
Q12. Retirement planning: "I am on track for my ideal retirement" — On track / Roughly / Behind / Far behind

**Scoring:** Each option maps to a score. Maximum score 60. Profile thresholds:
- Konservatif: 12–30
- Moderat: 31–45
- Agresif: 46–60

### Result Display

After question 12 is answered, a success box appears:
> "🎉 All questions answered!"

The risk profile is computed and shown:
- "Your Risk Profile: **Moderat**"
- "Score: 38/60 (63%)"
- Description text explaining what Moderat means

**Allocation table shown:**
| Instrument | Allocation |
|-----------|-----------|
| Deposito | 15% |
| ORI/SBR | 25% |
| Reksa Dana Pasar Uang | 10% |
| Reksa Dana Pendapatan Tetap | 20% |
| Reksa Dana Equity | 22% |
| REITs | 8% |

Session state updated: `risk_profile_set = True`

---

## Stage 5: Portfolio Recommendation

**Page:** Portfolio Recommendation (page 4 of 5)

**Entry condition:** Both `goal_set` and `risk_profile_set` must be True, otherwise warning shown

### Inputs (from session state)

- Goal: Property in Jakarta Selatan, Rp 2,415,000,000, 7 years
- Risk profile: Moderat
- Monthly contribution: from feasibility analysis (Rp 28,750,000 — the required amount to reach goal as stated)

### Computation

`build_portfolio()` called with `timeline_years = 7` (≥ 3, so no equity cap applied):

**Moderat allocation (7-year timeline):**
| Instrument | % | Monthly Amount (IDR) | Expected Return |
|-----------|---|---------------------|-----------------|
| Deposito | 15.0% | 4,312,500 | 4.5% |
| ORI/SBR | 25.0% | 7,187,500 | 6.5% |
| Reksa Dana Pasar Uang | 10.0% | 2,875,000 | 5.5% |
| Reksa Dana Pendapatan Tetap | 20.0% | 5,750,000 | 7.5% |
| Reksa Dana Equity | 22.0% | 6,325,000 | 12.0% |
| REITs | 8.0% | 2,300,000 | 10.0% |

**Blended return:** 7.79%
**Blended volatility:** 8.15%
**Projected value at year 7:** Rp 3,200,000,000 (exceeds goal by Rp 785M — this is the contribution as-calculated, not adjusted)

**Shortfall warning:** Because the ratio was 200% (RED), the required monthly is Rp 28,750,000 which exceeds the projected capacity. Shortfall shown: Rp 17.5B

### Growth Chart

Streamlit line chart showing year-by-year portfolio growth from Year 0 to Year 7. Goal amount shown in caption.

---

## Stage 6: Dashboard

**Page:** Dashboard (page 5 of 5)

**Shows:**
- Goal Set: ✅ Yes / ❌ Not yet
- Feasibility Analysed: ✅ Yes / ❌ Not yet
- Risk Profiled: ✅ Yes / ❌ Not yet

**If all three complete:**
- Goal summary (JSON)
- Feasibility summary (JSON)
- Risk profile (JSON)
- Balloon animation + "Your complete financial plan is ready!" message

---

## Green/Yellow/Red — What the User Sees

### Green Verdict (ratio < 30%)
**Feasibility page:**
- Badge: "🟢 Achievable"
- No scenario analysis shown
- Message: "Your goal is achievable with your current income and timeline. Proceed to Risk Profiler."

### Yellow Verdict (30–50%)
**Feasibility page:**
- Badge: "🟡 Achievable With Conditions"
- Scenario analysis shown with 2–3 scenarios
- Message: "Your goal is achievable but requires discipline. Review the adjustments below to improve your margin."

### Red Verdict (> 50%)
**Feasibility page:**
- Badge: "🔴 Not Achievable As Stated"
- Scenario analysis shown with all 4 levers (or fewer if blocked)
- If ratio ≥ 100%: "Scenario Optimizer Blocked" error shown with explanation
- Message: "As currently stated, this goal is not achievable. Review the scenarios below for viable adjustments."
