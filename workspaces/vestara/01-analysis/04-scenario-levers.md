# Scenario Lever Analysis: Priority Order Review

## Executive Summary

The four scenario levers (timeline extension, location adjustment, goal size reduction, monthly contribution increase) are mechanically sound but their default priority order is misaligned with how Indonesian financial planners actually approach distressed goals. The current ordering treats timeline extension as the default lever, but for five of seven goal types, this lever is culturally awkward or structurally incoherent. A financial planner would typically reverse the order, leading with contribution increase before touching timeline.

**Complexity: Moderate**

---

## Failure Point Register

| Risk                                                        | Likelihood | Impact | Severity    |
| ----------------------------------------------------------- | ---------- | ------ | ----------- |
| Timeline extension misapplied to fixed-deadline goals       | High       | Medium | Major       |
| Location change treated as independent lever                | Medium     | High   | Major       |
| Goal reduction dismissed as last resort                     | High       | Medium | Significant |
| Contribution increase recommended without income validation | Medium     | High   | Major       |
| Cultural context not reflected in lever weights             | High       | Medium | Significant |

---

## Lever-by-Lever Analysis

### Lever 1: Timeline Extension

**Current assumption**: Extending the horizon reduces monthly burden proportionally.

**Goal-type applicability**:

| Goal Type        | Natural Deadline?               | Timeline Extension Viable? | Notes                                                               |
| ---------------- | ------------------------------- | -------------------------- | ------------------------------------------------------------------- |
| Property         | No (but school enrollment ties) | Conditional                | Only if school enrollment dates are flexible                        |
| Education        | Yes (enrollment windows)        | **Poor fit**               | University admission dates are fixed; scholarship cycles are annual |
| Retirement       | No                              | **Best fit**               | Retirement age is soft; can work beyond 55                          |
| Emergency Fund   | Yes (unexpected)                | **Poor fit**               | Emergencies don't wait                                              |
| Wedding          | Yes (cultural/seasonal)         | **Limited fit**            | "Dua minggu lagi" pressure is real; families resist delays          |
| Higher Education | Yes (per semester)              | **Poor fit**               | Tuition installment schedules are rigid                             |
| Custom           | Depends                         | Conditional                | Depends on goal definition                                          |

**Indonesian cultural context**:

- Extended timelines for weddings create social friction. "Undangan sudah dicetak" is a real pressure.
- Parents often view education funding as non-negotiable — delaying child's education signals failure.
- Property timeline extension is most culturally acceptable (rental phase is normalized in urban areas).

**Verdict**: Timeline extension should be **downweighted** for fixed-deadline goals and **flagged** as requiring explicit justification when applied to wedding/education goals.

---

### Lever 2: Location Adjustment

**Current assumption**: Moving to a cheaper city or neighborhood reduces property goal cost.

**Critical questions**:

1. **Is the goal inherently location-tied?** A wedding in Surabaya cannot be held in Bandung without significant social cost. Education at a specific university is not interchangeable across cities.

2. **Does the user own the property goal, or are they renting/buying?** If the user wants to own property in Jakarta Selatan specifically, "buy in Bandung instead" is not a real alternative — it's a different goal.

3. **Are Indonesian cities fungible for the goal type?**
   - Property: Partially — housing markets are local; substituting Surabaya for Jakarta is a lifestyle change, not a financial optimization.
   - Education: No — a degree from Universitas Indonesia has different labor market value than Bandung's ITB.
   - Wedding: No — family ceremony location is culturally significant; destination weddings are outliers.

**Financial planner reality**: Location change is rarely the _first_ recommendation for property because:

- Transportation cost differences offset housing savings
- Children's school proximity matters
- Job location is often fixed (Jakarta commuters cannot easily relocate to Bandung)

**Verdict**: Location adjustment is a **real lever for property goals only**, and even then it is often a lifestyle trade-off rather than a pure financial optimization. It should not be treated as an independent lever applicable to all goal types.

---

### Lever 3: Goal Size Reduction

**Current assumption**: User can choose a smaller version of the goal.

**Goal-type applicability**:

| Goal Type        | Size Reduction Realistic? | Typical Reduction Approach                                   |
| ---------------- | ------------------------- | ------------------------------------------------------------ |
| Property         | Yes                       | Smaller sqm, farther location, used unit                     |
| Education        | Limited                   | Public university vs private, fewer semesters                |
| Retirement       | **Difficult**             | Lower retirement income target = lower dignity in retirement |
| Emergency Fund   | **No**                    | 6 months of expenses is not compressible                     |
| Wedding          | Limited                   | Guest list trimming has social cost; simpler venues          |
| Higher Education | Limited                   | Credit requirements are fixed; living cost reduction         |
| Custom           | Depends                   | Depends on goal definition                                   |

**Financial planner reality**: Goal reduction is often psychologically the hardest lever because:

- It feels like "giving up" on the goal
- For retirement, reducing the target signals fear rather than planning
- For weddings, social expectations create hard floors on cost

**Verdict**: Goal size reduction is underweighted in the current order. For many users, this is the most honest lever — acknowledging that the original goal may have been aspirational rather than necessary.

---

### Lever 4: Monthly Contribution Increase

**Current assumption**: User has disposable income they can redirect.

**The critical flaw**: This lever is only viable if the user's disposable income is actually positive. If the investment-to-income ratio puts them in Red (negative disposable income), increasing contribution is not a lever — it is already at maximum.

**Indonesian income context**:

- Young professionals in Jakarta have meaningful fixed costs (transport, rent, dependents)
- "Increase contribution" often means reducing quality of life, not shifting from savings
- Informal sector income (freelance, Gig economy) makes contribution increases volatile

**Income validation required**:

- Gross income vs net income (take-home pay after taxes, JHT, BPJS)
- Fixed obligations (rent, loans, remittances to family — common in Indonesian culture)
- Discretionary spending floor (transport, food minimums)

**Verdict**: Contribution increase should be **validated against actual disposable income** before presenting as a recommendation. For Red-verdict users, this lever may not exist.

---

## Recommended Lever Priority Order

Based on financial planner practice in Indonesian context:

| Priority | Lever                             | Rationale                                                       |
| -------- | --------------------------------- | --------------------------------------------------------------- |
| 1        | **Increase monthly contribution** | Most direct control; works if disposable income exists          |
| 2        | **Reduce goal size**              | Honest adjustment; psychologically hard but financially sound   |
| 3        | **Extend timeline**               | Works best for retirement/property; awkward for fixed deadlines |
| 4        | **Change location**               | Property-only; lifestyle trade-off, not pure optimization       |

**For Red-verdict users** (negative disposable income):

- Levers 1 and 4 are structurally unavailable
- The platform should recommend either: (a) goal size reduction, (b) timeline extension, or (c) advisory consultation before any scenario optimization

---

## Cross-Reference Audit

- **Goal model** (02-goal-model.md): Goal types have different deadline rigidity; the scenario optimizer does not account for this
- **Verdict engine** (03-verdict-engine.md): Red verdict (>100% ratio) triggers scenario optimizer, but optimizer does not check if levers are structurally available
- **Risk profiler**: Risk tolerance affects portfolio allocation, not scenario lever availability

---

## Implementation Implications

1. **Lever applicability matrix**: Scenario optimizer should maintain a goal-type × lever matrix defining which levers are valid for which goal types
2. **Disposable income floor check**: Before presenting contribution increase, calculate actual disposable income (net - fixed obligations - minimum food/transport)
3. **Location lever scoped to property**: Remove location as a generic lever; apply only when goal_type = "property"
4. **Timeline flagging**: When timeline is extended for wedding/education goals, display explicit warning about deadline rigidity

---

## Success Criteria

- [ ] Scenario optimizer validates lever availability before presenting options
- [ ] Property-specific location lever is clearly distinguished from generic location
- [ ] Red-verdict users receive distinct treatment path (advisory referral or goal restructuring, not scenario optimization)
- [ ] Timeline extension displays deadline-rigidity warning for wedding/education goals
