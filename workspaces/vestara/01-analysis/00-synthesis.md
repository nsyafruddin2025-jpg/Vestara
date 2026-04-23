# Vestara Analysis — Cross-Agent Synthesis

## Sources

- 01-competitive.md (value-auditor — pending)
- 02-thresholds.md (analyst-thresholds)
- 03-synthetic-data-risk.md (analyst-thresholds)
- 04-scenario-levers.md (analyst-failure)
- 05-failure-points.md (analyst-failure)
- Own analysis (team lead)

---

## 1. GOAL-FIRST DIFFERENTIATION

**Verdict: Partially defensible, narrow moat**

The gap vs Bibit/Pluang/Bareksa is real but shallow:

| App     | Goal-first?                          | Cost-specific? | Feasibility verdict? |
| ------- | ------------------------------------ | -------------- | -------------------- |
| Bibit   | Partial (risk tolerance → portfolio) | No             | No                   |
| Bareksa | No (product supermarket)             | No             | No                   |
| Pluang  | No (product-focused, gold/SGB)       | No             | No                   |

Vestara's actual differentiation: **cost specificity + honest feasibility verdict.** A user seeing "a 70sqm apartment in Surabaya costs Rp 1.12B, your salary covers 38% of the monthly payment → Yellow" is genuinely new.

**The vulnerability**: Bibit's parent (Stockbit/Sinarmas) has the data, distribution, and engineering capacity to build this in 6 weeks. The moat is not technical — it's先 mover data and user trust.

**Recommendation**: Lean into the cost database as the core asset. The goal framework is the hook; the city-specific cost data is the moat.

---

## 2. FEASIBILITY THRESHOLDS

**Verdict: Business judgment, not empirically grounded — needs recalibration**

The 30% Green boundary is derived from a Western heuristic (50/30/20 rule), not Indonesian empirical data.

Key finding from Bank Indonesia and BPS data:

- National household savings rate: ~30-34%
- Young urban professionals (25-35) in Jakarta: **8-18%** savings rate due to housing/lifestyle
- Bottom 40% income earners: **negative savings rate**

**The failure case**: A 25-year-old earning Rp 8M/month in Jakarta investing Rp 1.6M/month (20% of salary) gets **Green**. But their reality includes Rp 1.5M/month transport (motorcycle EMI + fuel), family contribution obligations, and irregular expenses — actual sustainable investment rate may be 10-12%.

**Three-part recommendation**:

1. **Income-bracket calibration**: Different thresholds per salary bracket (e.g., <Rp 10M: Green <20%, 10-20M: Green <30%, >20M: Green <40%)
2. **Goal-type calibration**: Emergency fund has a different risk profile than retirement — short horizon + high urgency
3. **City-tier calibration**: Jakarta costs consume a larger share regardless of discipline

---

## 3. SYNTHETIC TRAINING DATA

**Verdict: 99.9% accuracy is a red flag — ML adds zero value in current form**

The model achieves 99.9% accuracy because:

1. Labels are derived from the exact same formula as the primary feature (`investment_to_income_ratio`)
2. The model is essentially learning `if ratio < 0.30 → green` — which is the rule-based threshold
3. `investment_to_income_ratio` has 100% feature importance; all other features are zero

**What the professor will ask**: "What does your model know that your rule doesn't? If the answer is nothing, why did you use ML?"

**The structural fix**: Reframe as regression:

- Predict `months_to_achieve_goal` or `probability_of_success`
- The classifier becomes a post-processing step on top of a regression output
- This lets the ML add value: it can learn non-linear interactions between city cost index + income growth rate + timeline that a simple ratio formula misses

**Minimum defensibility for the course**:

- k-fold cross-validation (not single split)
- Show that model predictions diverge from rule-based threshold at boundary cases
- Add explicit "model vs rule comparison" table in presentation
- Acknowledge in presentation that 99.9% reflects data homogeneity, not model quality

---

## 4. SCENARIO LEVER PRIORITY

**Verdict: Priority order is wrong for 5 of 7 goal types**

| Lever                 | Current rank | Problem                                                                             |
| --------------------- | ------------ | ----------------------------------------------------------------------------------- |
| Extend timeline       | #1           | Misaligned for wedding (fixed date), education (enrollment windows), emergency fund |
| Change location       | #2           | Not actionable for non-property goals; for property it's a different goal           |
| Reduce goal size      | #3           | Psychologically hardest but financially most honest                                 |
| Increase contribution | #4           | Most painful; for Red users (>100% ratio) it's structurally impossible              |

**Failure point**: Scenario optimizer will recommend contribution increases for users whose disposable income is already negative — structurally impossible, not just difficult.

**Recommended reorder** (financial planner approach):

1. **Validate disposable income first** — hard gate: if ratio >100%, contribution lever is unavailable
2. **Goal size reduction** — psychologically hard but honest; show exactly what the user gives up
3. **Timeline extension** — viable for property and retirement; flagged as inappropriate for wedding/education
4. **Location change** — treat as "what if" exploration, not primary recommendation

**Indonesian cultural note**: Delaying a wedding ("undangan sudah dicetak" pressure) and education funding ("orang tua gagal membiayai") carry strong social stigma. The system should flag timeline extension for these goal types as high-friction.

---

## 5. STRUCTURAL FAILURE POINTS

### Critical (must fix before demo)

1. **Ratio >100% trap**: Scenario optimizer presents contribution increase when disposable income is negative. Fix: hard gate before optimizer activates.

2. **Income projection error**: 5%/year linear growth assumption fails in tech/consulting/oil & gas. Fix: income stress test at -50% and display confidence range.

### Major (should fix before production)

3. **Property price shock**: Jakarta Selatan can see 15-30% appreciation in 3 years. Fix: add 15% contingency buffer to property goals; show price sensitivity.

4. **Timeline <3 years with portfolio optimizer**: Equity allocation recommended regardless of horizon. Fix: cap equity at 40% for timelines <3 years; show warning.

5. **Currency risk for abroad education**: IDR depreciates 3-5%/year against AUD/EUR. Fix: add currency buffer to Higher Education goals.

### Significant (address in next sprint)

6. **Multi-goal competition**: System optimizes goals independently. A user with wedding + property goals needs sequencing. Fix: goal conflict detection and sequencing recommendation.

7. **City volatility tiers**: Bandung and Surabaya show higher property price volatility. Fix: flag high-volatility cities differently in cost estimates.

---

## 6. COC LOG ENTRIES NEEDED

After this analysis, the following decisions need to be documented in the COC log:

1. **Threshold calibration** — documented as business judgment call (Western heuristic adapted), not empirical Indonesian data. Recalibration by income bracket and goal type is a known gap.

2. **Synthetic data** — 99.9% accuracy acknowledged as a red flag; model refactored to regression form. Course presentation must acknowledge this limitation explicitly.

3. **Scenario lever priority** — reordered to: validate disposable income → goal size → timeline → location. Hard gate added for ratio >100%.

4. **Moat definition** — cost database is the core asset, not the goal framework. Competitive differentiation is narrow and time-bounded.

---

_Synthesis complete. Full individual reports in 01-analysis/. Competitive analysis (01-competitive.md) pending from value-auditor agent._
