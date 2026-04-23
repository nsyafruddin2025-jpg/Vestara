# 002 — Edge Case Flows

## Edge Case 1: Salary Below Living Cost (Ratio > 100% Immediately)

**Trigger:** `monthly_salary < monthly_living_cost` for the selected city

**Example:** Aditya earns Rp 6,000,000/month in Jakarta where living cost is Rp 8,500,000/month

**Flow:**
1. User enters salary Rp 6,000,000 in Feasibility Analysis
2. `compute_feasibility()` computes:
   ```
   disposable = 6,000,000 − 8,500,000 = −2,500,000 (negative)
   disposable capped at 1 for ratio computation
   ratio = min(monthly_required / 1, 2.0) → capped at 200%
   ```
3. Verdict immediately: **Red**
4. `run_scenario_analysis()` is called
5. **Hard gate triggers:** `ratio >= 100%` → blocked_reason returned
6. UI shows:
   > "⚠️ Scenario Optimizer Blocked"
   > "Your required monthly investment exceeds your entire disposable income. Please consider: (1) reducing your goal size, or (2) exploring a lower-cost city or neighbourhood. Increasing your monthly contribution is not structurally available when disposable income is fully consumed."

**What user can do:**
- Change city to a cheaper one (Yogyakarta living cost Rp 4,000,000 → disposable becomes Rp 2,000,000)
- Choose a smaller goal
- No scenario lever is available to increase contribution

**Session state:** `feasibility_result` stored with verdict=red, ratio capped at 2.0

---

## Edge Case 2: Timeline Less Than 1 Year

**Trigger:** User sets `timeline_years < 1` (slider minimum is 1)

**Example:** Aditya wants to buy a wedding venue in 6 months

**Flow:**
1. `GoalBuilder` accepts timeline = 1 year (floor enforced by slider, minimum 1)
2. `compute_feasibility()`:
   ```
   monthly_required = goal_cost / (1 × 12) = goal_cost / 12
   For Rp 80,000,000 wedding: monthly_required = 6,667,000/month
   With disposable 3,500,000: ratio = 190% → Red
   ```
3. Timeline slider cannot go below 1 year — the system enforces this structurally

**What user sees:**
- Wedding goal with 1-year timeline is almost always Red (ratio very high)
- Scenario optimizer recommends: location change (most effective) or goal reduction
- Timeline lever is blocked for Wedding (fixed-deadline goal) anyway

**Special handling for Wedding:**
- Wedding goal-type has `timeline_locked = True` and `TIMELINE_MAX_YEARS = 5`
- The scenario optimizer will never recommend timeline extension for Wedding
- Wedding with timeline > 5 years is a warning: "A wedding more than 5 years away may not align with typical planning horizons"

---

## Edge Case 3: Custom Goal With No Cost Estimate

**Trigger:** User selects "Custom" goal type, chooses "Describe your goal and I'll help estimate", enters no amount

**Example:** "I want to start a café franchise" with no estimated cost and no target amount

**Flow:**
1. `build_goal()` with `custom_amount = 0 or None`:
   ```python
   if custom_amount:
       cost = custom_amount
   else:
       description = "Custom financial goal: I want to start a café franchise"
       cost = 0  # no estimate
   ```
2. `GoalProfile` returned with `estimated_cost = 0`
3. Feasibility page shows `Goal Amount: Rp 0` (potentially confusing)
4. `compute_feasibility()` with `goal_cost = 0`:
   ```
   monthly_required = 0 / (timeline × 12) = 0
   ratio = 0 / disposable = 0 → GREEN
   ```
5. This is technically correct (a Rp 0 goal is always achievable) but misleading

**What the system does:**
- When `goal_cost = 0`, the UI should show a warning: "Please enter a target amount to get a meaningful feasibility analysis"
- The "Custom" goal type's second path ("Enter a target amount directly") should be encouraged for users with specific amounts
- The description-based path is intentionally fuzzy and is meant for users who genuinely don't know their cost — the AI assistant estimation flow is a future enhancement (not in MVP)

**Session state:** `goal_profile` stored with `estimated_cost = 0`; no validation prevents proceeding

---

## Edge Case 4: Wedding Goal With Fixed Date That Cannot Be Extended

**Trigger:** User plans a wedding for exactly 2 years from now (fixed cultural/family date), goal-type is Wedding

**Example:** Aditya's girlfriend's family has already booked the venue for December 2028, 30 months away. Aditya wants a "Grand/Bilingual" wedding (Rp 200M).

**Flow:**
1. `build_goal()` with `goal_type = "Wedding"`, `wedding_scale = "Grand/Bilingual"`, `timeline_years = 2.5` (slider allows fractional, displayed as years)
2. `estimated_cost = Rp 200,000,000`
3. `run_scenario_analysis()` called with `goal_type = "Wedding"`:
   - `goal_modifier["timeline_locked"] = True` → timeline optimizer skipped
   - `income_bracket = "mid_career"` → green_threshold = 32% (30% base + 2% Wedding modifier)
4. `compute_feasibility()`:
   ```
   monthly_required = 200,000,000 / 30 = 6,667,000/month
   disposable = 3,500,000
   ratio = 190% → Red
   ```
5. `run_scenario_analysis()` with `goal_type = "Wedding"`:
   - **TIMELINE lever skipped** (timeline_locked=True)
   - Only LOCATION, GOAL_SIZE, MONTHLY_CONTRIBUTION available
   - Location change: cheapest city Medan → Rp 3,500,000 disposable → still Red
   - Goal reduction: needs to reduce by 81% → only affordable at Rp 38,000,000
   - Contribution increase: blocked (ratio 190% > 100%)

**What user sees:**
- Red verdict with only 1 viable scenario: reduce goal from Rp 200M Grand wedding to ~Rp 38M
- Timeline expander is **not shown** (it's locked for Wedding)
- Warning: "Wedding goals have a fixed date and cannot be extended. Consider reducing goal size or exploring a lower-cost city."

---

## Edge Case 5: Abroad Education With IDR Depreciation Risk

**Trigger:** User plans Higher Education in the US for a Master's degree (2 years)

**Example:** Karina, 24, Rp 15M/month salary, wants to study at a Top 50 university in the US

**Flow:**
1. `build_goal()` with `goal_type = "Higher Education"`, `country = "US"`, `tier = "Top 50 Global"`, `degree = "Master's Degree"`
2. `estimate_higher_education_cost()` computes:
   ```
   base_annual_map["US"] = (150,000,000, 350,000,000)
   mid = (150M + 350M) / 2 = 250,000,000
   degree_years = 2
   tier_multiplier["Top 50 Global"] = 1.3
   base_cost = 250,000,000 × 2 × 1.3 = 650,000,000

   # C5 buffer applied:
   IDR_DEPRECIATION_RATE = 4%/yr
   ABROAD_BUFFER = 10%
   depreciated = 650,000,000 × (1.04)² × 1.10
               = 650,000,000 × 1.0816 × 1.10
               = 772,792,000
   ```
3. `estimated_cost = Rp 772,792,000` (not Rp 650,000,000 — buffer added)
4. Feasibility: ratio = 36.8% → **YELLOW** (without buffer, would have been 30.9% → GREEN)

**Why this matters:**
Without the currency depreciation buffer (the C5 fix), the system would have told Karina she was Green when the actual cost in IDR terms at the time of studying would be Rp 772M — a 19% understatement. A Yellow verdict is more honest and gives her time to plan.

**What user sees:**
- Higher Education Abroad cost is ~19% higher than the raw estimate
- Yellow verdict triggers scenario analysis
- Scenario recommends: extend timeline to 3 years, reduce to a Public/State university (Tier 1), or find scholarship to reduce base cost

---

## Edge Case 6: User With Multiple Conflicting Goals

**Trigger:** User tries to plan two goals simultaneously — Property (Rp 2.4B in 7 years) and Higher Education (Rp 600M in 4 years)

**Current state (MVP limitation):**
The system handles one goal at a time. Session state stores a single `goal_profile`. If a user completes Property goal and then starts Higher Education, the Property session state is overwritten.

**What the UI shows:**
- No explicit warning when starting a second goal
- The Dashboard shows only the most recent goal's JSON
- Portfolio Recommendation uses only the most recent goal's profile

**Implications:**
- A user planning both goals would need to run the flow twice
- The system cannot compute whether the combined monthly investment exceeds disposable income
- This is a known MVP gap (T7 — multi-goal tracking) deferred to post-MVP

**What the user would need to do manually:**
1. Run Property goal → get required monthly: Rp 28,750,000
2. Run Higher Education goal → get required monthly: Rp 18,750,000
3. Combined: Rp 47,500,000/month vs. disposable Rp 3,500,000/month → ratio 1,357% → clearly impossible
4. User would need to prioritize or phase the goals

**Future enhancement (Phase 2):**
Multi-goal dashboard showing:
- Each goal's monthly requirement
- Combined ratio vs. disposable
- Which goals are in conflict
- Suggested goal sequencing (e.g., "Complete Emergency Fund first, then Property, then Higher Education")

---

## Edge Case 7: Zero Disposable Income

**Trigger:** `monthly_salary == monthly_living_cost` exactly

**Example:** User earns exactly Rp 8,500,000/month in Jakarta Selatan

**Flow:**
1. `compute_feasibility()`:
   ```python
   disposable = max(monthly_salary - monthly_living_cost, 1)
   # disposable = max(0, 1) = 1
   ratio = min(monthly_required / 1, 2.0) = capped at 200%
   ```
2. `run_scenario_analysis()`: hard gate triggers, blocked_reason shown
3. UI: "Your required monthly investment exceeds your entire disposable income"

**The `max(..., 1)` fix:**
The code caps negative disposable at 1 (not 0) to avoid division-by-zero errors. A ratio of 200% (capped) is shown, which is the correct semantic — if you have zero disposable income, your required investment is infinitely more than your capacity.

---

## Edge Case 8: Extreme Timeline (40 Years)

**Trigger:** User sets timeline to maximum (40 years) for retirement

**Example:** User is 25, plans to retire at 65, timeline = 40 years

**Flow:**
1. `GoalBuilder` with `goal_type = "Retirement"`: timeline computed as `retirement_age − current_age = 65 − 25 = 40`
2. `estimate_retirement_cost()`: annual expense × years
3. `compute_feasibility()`:
   ```
   monthly_required = goal_cost / 480 (40 × 12)
   ratio typically very low for 40-year timeline → GREEN
   ```
4. Scenario optimizer: `optimize_timeline()` tries to extend from 40 years, but `TIMELINE_MAX_YEARS["Retirement"] = 40`, so loop finds no valid extension

**What user sees:**
- Green verdict (typically)
- No timeline scenario shown (already at maximum)
- Contribution scenario shown if ratio > green threshold (rare for 40-year timeline)

---

## Edge Case 9: Invalid City Selection

**Trigger:** City is not found in `LIVING_COST_MONTHLY` dictionary

**Example:** User enters custom text in the city field (dropdown prevents this in UI, but API caller could pass invalid city)

**Flow:**
```python
monthly_living = LIVING_COST_MONTHLY.get(city, 6_000_000)  # fallback to 6M
```
The system uses a default fallback of Rp 6,000,000/month (roughly Yogyakarta-level) for any unknown city.

**What this means:**
- A user in "Unknown City" gets the Yogyakarta living cost estimate
- This is conservative — it underestimates living cost for expensive cities and overestimates for cheap ones
- The UI dropdown prevents this in normal usage; it could only happen via direct API call

**Session state:** `goal_profile["city"]` stores the raw string, even if not in the known cities list
