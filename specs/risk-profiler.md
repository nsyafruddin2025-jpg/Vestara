# Risk Profiler — Spec

## Questionnaire

12 questions, 8 dimensions. Each question has 5 options scored 1-5.

### Dimension Mapping

| Question              | Dimension             | Max Score |
| --------------------- | --------------------- | --------- |
| q1_horizon            | investment_horizon    | 5         |
| q2_loss_reaction      | loss_tolerance        | 5         |
| q3_income_stability   | income_stability      | 5         |
| q4_dependents         | financial_obligations | 5         |
| q5_debt               | debt_burden           | 5         |
| q6_investment_exp     | investment_experience | 5         |
| q7_volatility_comfort | volatility_tolerance  | 5         |
| q8_liquidity          | liquidity_need        | 5         |
| q9_emergency_fund     | emergency_fund_status | 5         |
| q10_goal_urgency      | goal_urgency          | 5         |
| q11_knowledge         | financial_knowledge   | 5         |
| q12_recurring_invest  | discipline            | 5         |

Max total score: 60

## Profile Classification

```
Konservatif: 12-30 (20-50th percentile)
Moderat: 31-45 (51-75th percentile)
Agresif: 46-60 (76-100th percentile)
```

## Score Interpretation

The score represents risk tolerance and investment capacity on a spectrum:

- 12 = minimum risk tolerance (guaranteed returns only)
- 60 = maximum risk tolerance (willing to accept significant volatility)

##印尼-profile Labels (OJK-Aligned)

Profiles align with OJK's risk classification framework for investment products:

- **Konservatif**: "Low risk" — suitable for capital preservation
- **Moderat**: "Medium risk" — balanced growth and preservation
- **Agresif**: "High risk" — growth-oriented

## Profile to Allocation Contract

```
risk_profile: Konservatif
→ allocation: deposits 25-35%, bonds 35-45%, reksa_dana_equity 0-5%
→ max_equity_exposure: 5%
→ max_reits_exposure: 5%

risk_profile: Moderat
→ allocation: deposits 10-20%, bonds 20-30%, reksa_dana_equity 15-25%
→ max_equity_exposure: 25%
→ max_reits_exposure: 10%

risk_profile: Agresif
→ allocation: deposits 0-5%, bonds 5-10%, reksa_dana_equity 50-65%
→ max_equity_exposure: 65%
→ max_reits_exposure: 25%
```

## Session State Contract

```
st.session_state["risk_answers"]: dict[str, int]  # question_id → score
st.session_state["risk_page"]: int  # current page (0-based)
st.session_state["risk_profile"]: RiskProfile | None  # set after completion
st.session_state["risk_profile_set"]: bool
```

## Question Presentation

- 3 questions per page
- Progress bar showing completion fraction
- Must answer all questions before proceeding to portfolio
- Cannot revisit after submission (answers are final for this session)
- Back navigation allowed within a session

## Validation Rules

1. All 12 questions must be answered
2. Scores must be integers 1-5
3. Profile calculation is deterministic (same answers = same profile)
4. Profile must be recalculated if any answer changes
