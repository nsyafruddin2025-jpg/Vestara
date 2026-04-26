# Goal-First vs Product-First, Regression vs Classification, Synthetic vs Real Data

## Goal-First vs Product-First

### Product-First (Industry Standard)

Most investment platforms start with the product (a portfolio, a fund, a return) and work backwards to how it fits a user's life.

**Bibit, Pluang, Bareksa** all follow this pattern:
1. User browses available funds/portfolios
2. User selects a risk profile or investment theme
3. Platform shows projected returns
4. User maps this to a life goal (if at all)

**Problems with product-first:**
- User must know what they want before they know what they need
- No connection between investment choice and life goal
- Financial anxiety: too many options, no clear "right answer"
- Goals that don't fit standard products get abandoned

### Goal-First (Vestara's Approach)

Vestara starts with the life goal and works backwards to the investment strategy.

1. User describes their life goal (property, retirement, education)
2. Platform estimates the real cost in today's rupees
3. Platform analyses feasibility: can this person actually achieve this?
4. Platform builds a risk profile from actual behaviour questions
5. Platform recommends an illustrative portfolio calibrated to the goal

**Advantages:**
- Clear "right answer" for each user: the allocation that matches their goal + risk
- Emotional connection: the goal is concrete, not abstract returns
- Motivation: seeing your goal cost makes the monthly contribution feel purposeful
- Compliance: educational tools, not personalised advice (POJK 21/2011 Path B)

**Disadvantages:**
- Cost estimation is inherently uncertain (no real-time property data)
- Goal-first requires more upfront data entry from user
- Synthetic data limits accuracy of feasibility analysis

---

## Regression vs Classification

### Classification Approach (What Bibit/Plunk Likely Use)

Training data: labelled user profiles → recommended portfolio
- User answers questions → model classifies into risk bucket → maps to product

**Advantages:**
- Can leverage real user behaviour data if available
- Personalised at scale once model is trained
- Industry-standard ML approach

**Challenges for Vestara:**
- Need real user data to train ( Vestara has none)
- Labelling is subjective: what is the "right" portfolio for a profile?
- Regulatory: classification-based advice is regulated (POJK 21/2011)

### Regression Approach (Vestara's Approach)

Training data: historical instrument returns → project future value
- User's goal amount and timeline → required monthly contribution
- Required contribution + risk profile → illustrative allocation

**Advantages:**
- Interpretable: user can see exactly how the numbers work
- No training data needed: purely rules-based on market assumptions
- Regulatory safe: no model predicting "right" answer, just illustrating projections
- Easy to explain: "we assumed 4.5% annual return on deposits"

**Disadvantages:**
- Assumes historical returns persist (conservative estimates mitigate this)
- Doesn't personalise to individual behaviour beyond risk profile
- Cannot adapt to individual financial patterns

### Decision: Regression for MVP

Vestara uses regression because:
1. No real user data → classification model would be meaningless
2. Regulatory pathway B requires demonstrable education focus, not advice
3. Transparency: users should understand the assumptions, not trust a black box
4. Synthetic data: regression works on synthetic cost estimates; classification would need real outcomes

---

## Synthetic vs Real Data

### Why Synthetic Data

**What we have:**
- Property price per sqm by city (publicly available, approximated)
- School fees (publicly available, approximated)
- Living costs by city (publicly available, approximated)
- Instrument return assumptions (publicly available historical data)
- Risk profile correlation data (synthetic, no real user data)

**What we don't have:**
- Real user financial profiles
- Real outcome data (did users who的目标 X actually achieve it?)
- Real property transactions by city/neighbourhood
- Real investment performance by instrument

### Synthetic Data Limitations

| Area | Synthetic limitation | Impact |
|------|---------------------|--------|
| Property costs | &#177;15-20% uncertainty | Goal amount could be significantly off |
| Return assumptions | Conservative but static | Doesn't adapt to market regime changes |
| Risk profiles | Theoretical not behavioural | May not reflect actual user risk tolerance |
| Feasibility | No individual income patterns | Crude monthly salary vs living cost ratio |

### Mitigations Applied

1. **Explicit uncertainty ranges** — data freshness warnings on every estimate
2. **Conservative return assumptions** — 4.5-12% vs optimistic 15-20%
3. **Regulatory disclaimer** — educational tool, not financial advice
4. **Conservative thresholds** — 30% investment-to-disposable ratio (vs aggressive 50%+)

### What Real Data Would Change

If Vestara had real data:
- Property costs: real transaction prices by neighbourhood, not city averages
- Feasibility: ML model trained on actual user outcomes, not rule-based ratio
- Risk profiles: behavioural data validating the 12-question approach
- Portfolios: actual performance tracking, not illustrative projections
