# Structural Failure Points

## Executive Summary

The scenario optimizer and portfolio engine have significant structural vulnerabilities when operating at the boundaries of the input space: negative disposable income (Red verdict >100%), compressed timelines under 3 years, property price shocks in specific cities, and income projection errors compound to produce misleading recommendations. The system treats inputs as stable when they are inherently uncertain, and does not propagate uncertainty through to outputs.

**Complexity: Complex**

---

## Failure Point Register

| Failure Point                              | Likelihood | Impact | Severity    |
| ------------------------------------------ | ---------- | ------ | ----------- |
| Property price shock in single city        | Medium     | High   | Major       |
| Income projection error                    | High       | High   | Critical    |
| Ratio >100% with no actionable levers      | High       | High   | Critical    |
| Timeline <3 years with portfolio optimizer | Medium     | High   | Major       |
| Goal cost estimation edge cases            | Medium     | Medium | Significant |
| Portfolio optimizer on compressed timeline | High       | High   | Major       |
| Currency/inflation mismatch                | Low        | High   | Major       |
| Multi-goal interaction (competing goals)   | Medium     | Medium | Significant |

---

## Failure Point 1: Property Price Shock

**Scenario**: User sets a property goal for Jakarta Selatan. Over 3 years, Jakarta Selatan property prices rise 30% (common in proximity to new MRT stations).

**What the system does**:

- Calculates initial ratio based on current property price estimate
- If Green, user proceeds; scenario optimizer never triggered
- If Yellow, scenario optimizer recommends timeline extension or contribution increase

**What actually happens**:

- Property price rises faster than income growth assumption (typically 5%/year wage growth vs 15-30%/year property appreciation in prime locations)
- User reaches the goal date with insufficient funds
- The scenario optimizer's "optimal path" was calculated against a price that no longer exists

**Specific Indonesian context**:

- Jakarta Selatan, Jakarta Pusat, and Surabaya CBD have shown 20-40% cumulative appreciation over 3-year periods (2019-2022 data)
- Tier-2 cities (Medan, Makassar) show higher volatility with less liquid markets
- "Subsidi rumah" (government subsidy) programs create artificial price floors in certain segments

**Failure mode**: The system recommends a path to a goal cost that becomes unreachable before the path is complete.

**Mitigation**:

- Display property price sensitivity: "If prices rise 10%, your timeline extends by X months"
- Include buffer in goal cost estimate (e.g., 15% contingency for property goals)
- Flag cities with high historical volatility (bandung, Surabaya) differently from stable markets

---

## Failure Point 2: Income Projection Error

**Scenario**: User works in tech/consulting/oil & gas — industries with high income volatility. A layoff or industry downturn reduces income by 40% mid-journey.

**What the system does**:

- Uses current income as baseline for all future projections
- Assumes linear growth at 5%/year (default assumption)
- Scenario optimizer calculates contribution requirements based on projected income

**What actually happens**:

- Layoff: income drops to zero or 60% (severance)
- Industry collapse (e.g., coal mining 2015-2016, oil & gas 2020): sustained depression
- Career transition: 6-12 month income gap during onboarding

**Indonesian income realities**:

- BPJS Ketenagakerjaan covers only a fraction of wages for formal sector; informal sector has no unemployment protection
- Probation periods (3 months) during which termination is instant
- "Resign with nothing" culture means income gap can be abrupt

**Failure mode**: The scenario optimizer's contribution path assumes income continuity that is not guaranteed. Users may commit to increased contributions based on a projection that becomes invalid within months.

**Mitigation**:

- Stress test at 50% income reduction: "Can you still meet contributions if your income drops by half?"
- Flag industries with high income volatility (mining, tech startups, oil & gas, hospitality)
- Recommend Emergency Fund goal as prerequisite before property goal
- Display "months of runway" metric: how many months can contributions continue if income stops

---

## Failure Point 3: Ratio >100% — The Disposed Income Trap

**Scenario**: User has investment-to-income ratio of 140% (e.g., Rp 10 million monthly income, Rp 14 million monthly goal contributions required).

**What the system does**:

- Verdict engine outputs "Red"
- Scenario optimizer activates to find a path to Green
- Lever 1 (increase contribution) is presented as viable option

**What is wrong**:

- If ratio is >100%, the user already has negative disposable income
- Increasing contribution is structurally impossible — there is no more income to redirect
- The scenario optimizer is presenting an invalid lever

**Edge case**: What if the user "has more income" in the sense of credit? The system should not recommend going into debt to fund a goal.

**Failure mode**: Scenario optimizer provides recommendations that cannot be executed, leading to user frustration and potential debt.

**Mitigation**:

- **Gate before optimizer**: If ratio >100%, do not activate scenario optimizer. Instead, display: "Your current goals require more than your take-home income. We recommend: [1] reducing goal size, [2] prioritizing one goal, [3] consulting a financial advisor"
- **Credit assumption exclusion**: The system should not assume credit (KTA, Kredit Pemilikan Rumah) as a contribution source unless explicitly modeled
- **Priority ranking**: For multi-goal users with >100% ratio, recommend goal prioritization rather than simultaneous pursuit

---

## Failure Point 4: Portfolio Optimizer on Compressed Timeline (<3 years)

**Scenario**: User has 2 years to accumulate Rp 200 million for a wedding goal. Risk profiler returns "Agresif".

**What the system does**:

- Portfolio optimizer allocates to high-equity instruments (saham, reksa dana saham)
- Recommends 80-90% equities, 10-20% fixed income

**What actually happens**:

- Equity markets are volatile over 2-year horizons; a 30% drawdown in year 2 leaves user with insufficient funds
- Saham and reksa dana saham are not suitable for short horizons regardless of risk tolerance
- Time horizon is the dominant factor in portfolio allocation, not risk tolerance

**Financial planning consensus**: Asset allocation should be 60-40 (equity-debt) at 3-5 year horizon; pure equity is appropriate only for 7+ year horizons.

**Indonesian instrument context**:

- Saham (stocks): appropriate for 5+ year horizons
- Reksa dana campuran (balanced funds): appropriate for 3-5 year horizons
- Reksa dana pasar uang (money market): appropriate for <2 year horizons
- Deposito (time deposits): appropriate for <1 year horizons
- Emas (gold): volatile but stores value; not a growth instrument

**Failure mode**: The portfolio optimizer produces a recommendation that maximizes expected value but has unacceptable downside risk given the compressed timeline.

**Mitigation**:

- **Hard floor**: If timeline <3 years for non-retirement goals, cap equity allocation at 40%
- **Warning display**: "Your timeline of X months is shorter than typically recommended for aggressive allocation. We have capped your equity exposure at 40%."
- **Separate allocation model for short horizons**: Short-horizon goals should use liability-driven investing (match the goal cost date, not maximize return)

---

## Failure Point 5: Goal Cost Estimation Edge Cases

**Property goal edge cases**:

- **Land + construction vs apartment**: Land prices appreciate; apartment prices are correlated with developer's financial health
- **Off-plan vs ready**: Off-plan (pra-pasaran) is 20-30% cheaper but carries developer default risk
- **Location within city**: "Jakarta Selatan" spans from Kemang to Bintaro; price range is 3x within the same postal code

**Education cost edge cases**:

- **International vs domestic**: Medical school abroad (Filipina, Malaysia) costs Rp 500M+; domestic medical school Rp 150M
- **Scholarship dependency**: Assumptions about scholarship renewal create multi-year uncertainty
- **Currency risk for overseas**: Rp depreciation on top of tuition increases effective cost

**Retirement cost edge cases**:

- **Inflation assumption**: 4% assumed inflation compounds to 2.7x over 20 years; a Rp 50M/year retirement need becomes Rp 135M/year in today's money
- **Healthcare cost escalation**: Indonesian healthcare costs rise faster than general inflation (8-12%/year for premium care)

**Wedding cost edge cases**:

- **"Maternal family" costs**: In some cultures, maternal family costs are separate from paternal — effectively 1.5-2x the stated budget
- **Seasonal pricing**: Venue costs 2x during "musim weddings" (June-August, December); dates outside peak are significantly cheaper
- **Social expectation floor**: Guest list tends to grow, not shrink; "smaller wedding" recommendations hit cultural resistance

---

## Failure Point 6: Multi-Goal Interaction

**Scenario**: User has both a property goal (60 months) and a wedding goal (12 months) with limited income.

**What the system does**:

- Calculates ratio independently for each goal
- Scenario optimizer handles each goal in isolation

**What actually happens**:

- Property contribution requirements compete with wedding savings
- User must choose which goal to prioritize
- Treating goals independently leads to both being underfunded

**Indonesian context**:

- "Hadiah nikah" (wedding gifts) can partially fund property — system does not model this
- Family contributions (orang tua bantu]) are common but not modeled
- Graduated goals: users often sequence goals (wedding first, then property) rather than pursuing simultaneously

**Failure mode**: Simultaneous optimization of competing goals produces allocations that are individually optimal but collectively unachievable.

**Mitigation**:

- **Multi-goal priority ranking**: Ask user to rank goals; allocate income in priority order
- **Sequence detection**: If property goal is 5+ years and wedding is <2 years, recommend sequencing rather than simultaneous pursuit
- **Gift/ Contribution modeling**: Include optional "expected family contribution" field

---

## Failure Point 7: Currency and Inflation Mismatch

**Scenario**: User plans education in Australia (AUD-denominated costs) with Indonesian income (IDR).

**What the system does**:

- Converts AUD tuition to IDR at current exchange rate
- Projects forward at current exchange rate

**What actually happens**:

- IDR has depreciated ~3-5% per year against AUD over the past decade
- A Rp 200M equivalent today costs Rp 350M+ in 10 years at historical depreciation rates
- Exchange rate risk compounds with inflation risk

**Indonesian context**:

- overseas education costs have effectively doubled in IDR terms over 10 years for families who did not hedge
- Golden visa and dualcurrency options exist but are not mainstream

**Failure mode**: Overseas education costs are systematically underestimated due to exchange rate depreciation.

**Mitigation**:

- Apply currency depreciation buffer (minimum 2% per year) for overseas goals
- Display costs in both IDR and target currency for overseas goals
- Flag "exchange rate risk" as a separate risk dimension for overseas goals

---

## Summary: System Behavior at Boundaries

| Input Condition             | Current Behavior                                        | Correct Behavior                                      |
| --------------------------- | ------------------------------------------------------- | ----------------------------------------------------- |
| Ratio >100%                 | Scenario optimizer runs, presents contribution increase | Block optimizer; show priority/goal-reduction path    |
| Timeline <3 years           | Full equity allocation for Agresif                      | Cap equity at 40%; show warning                       |
| Property in volatile city   | Standard confidence                                     | Show price volatility warning; add contingency buffer |
| Overseas education          | IDR equivalent at spot rate                             | IDR + currency depreciation buffer                    |
| Multi-goal conflict         | Independent optimization                                | Priority ranking; sequence detection                  |
| Income in volatile industry | Linear growth projection                                | Stress test at 50% reduction                          |

---

## Implementation Implications

1. **Input validation layer**: Before scenario optimizer runs, validate that the input space is within the actionable region (ratio <100%, timeline >= 3 years for non-retirement goals)
2. **Stress testing**: Run scenario optimizer outputs through a stress test (income -50%, property prices +20%, market -30%) before presenting
3. **Confidence intervals**: Display goal costs and timelines with confidence ranges, not point estimates
4. **Goal sequencing engine**: For multi-goal users with conflicting requirements, recommend priority order rather than simultaneous pursuit
5. **Risk disclosure layer**: When the system recommends an action that has high downside risk (compressed timeline + aggressive allocation), display explicit risk disclosure

---

## Cross-Reference Audit

- **Scenario levers** (04-scenario-levers.md): Contribution increase lever is invalid when ratio >100%; timeline extension is invalid for compressed horizons
- **Goal model** (02-goal-model.md): Goal costs are point estimates; edge cases section identifies where estimation is particularly uncertain
- **Verdict engine** (03-verdict-engine.md): Verdict is binary (Green/Yellow/Red) without propagating input uncertainty through to recommendation confidence
- **Portfolio optimizer**: Assumes time horizon is sufficient for equity allocation; does not cap based on actual timeline
