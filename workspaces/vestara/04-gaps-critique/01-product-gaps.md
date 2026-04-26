# Honest Product Gaps

## Critical Gaps (Before Demo)

### 1. No User Accounts
**What it is:** Vestara is stateless. Every page refresh loses all session state.
**Impact:** Cannot demo multi-session workflows; no persistence between visits.
**Fix needed:** Add Streamlit authentication or session persistence.
**Priority:** P0 for demo — session state loss is embarrassing.

### 2. No Real Property Data
**What it is:** Property costs are city-level averages, not neighbourhood-level real data.
**Impact:** Cost estimates could be &#177;30-50% off for specific neighbourhoods.
**Fix needed:** Integrate with real property API (Rumah123, 99.co, or government data).
**Priority:** P1 — acceptable for MVP demo if disclaimer is prominent.

### 3. No Product Execution
**What it is:** Vestara shows illustrative allocations but cannot execute any investment.
**Impact:** Users who want to act must go to Bibit/Plung to execute.
**Fix needed:** Partner with fund distribution platform (Ajaib, Bibit API) or get POJK license.
**Priority:** P1 — disclosed as educational, but limits engagement.

### 4. No Email/Export
**What it is:** No way to save or share a financial plan.
**Impact:** Vestara plans exist only in the Streamlit session.
**Fix needed:** Add PDF export or email plan summary.
**Priority:** P2 — nice to have for MVP.

---

## Important Gaps (Post-MVP)

### 5. No Inflation Adjustment
**What it is:** Goal costs are shown in today's rupees, not future value.
**Impact:** A Rp 500M property goal in 10 years is actually ~Rp 740M at 4% inflation.
**Fix needed:** Add inflation-adjusted goal amounts.
**Priority:** P2 — should be visible to users who ask "will this still be enough in 10 years?"

### 6. No Tax Planning
**What it is:** No consideration of tax implications on investment returns or withdrawal.
**Impact:** Actual take-home could be significantly lower than projected.
**Fix needed:** Add basic capital gains tax, PPh 23, and withholding tax estimates.
**Priority:** P2 — Indonesian tax rules are complex but calculable.

### 7. No Multi-Goal Planning
**What it is:** Users can only plan one goal at a time.
**Impact:** Someone with both retirement and children's education goals must plan separately.
**Fix needed:** Multi-goal portfolio with priority weighting.
**Priority:** P2 — single goal is fine for MVP demo.

### 8. No Income Growth Modelling
**What it is:** Monthly salary is static; income growth slider exists but isn't connected to feasibility.
**Impact:** Users with growing income may be told "not achievable" when they actually are.
**Fix needed:** Connect income growth rate to feasibility calculation across timeline.
**Priority:** P2 — income growth slider exists but isn't wired.

### 9. No Investment Return Projection with Contributions
**What it is:** Growth chart shows compound growth but doesn't distinguish contributions from returns.
**Impact:** Users may overestimate what investment returns alone achieve.
**Fix needed:** Decompose projected value into: (1) contributions, (2) investment returns.
**Priority:** P2 — adds educational value.

---

## Nice to Have (Future)

### 10. No Multi-Instrument Simulation
Users cannot adjust individual allocation percentages and see impact.

### 11. No Tax-Advantaged Accounts
No consideration of Taspen, BPJS, or corporate pensions.

### 12. No Currency Hedging
No consideration of IDR/USD exposure for education abroad goals.

### 13. No Geospatial Visualisation
Property goals shown as text; no map view of affordable areas.
