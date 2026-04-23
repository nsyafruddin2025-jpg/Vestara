# Portfolio Optimizer — Spec

## Instrument Universe

All Indonesian OJK-regulated instruments suitable for retail investors:

| Instrument                  | Type            | Liquidity                 | Expected Return | Volatility | Minimum Horizon |
| --------------------------- | --------------- | ------------------------- | --------------- | ---------- | --------------- |
| Deposito                    | Fixed income    | Low (locked term)         | 4-5%/yr         | ~0%        | 1-3 months      |
| ORI / SBR                   | Government bond | Medium (secondary market) | 6-7%/yr         | 3-5%       | 1 year          |
| Reksa Dana Pasar Uang       | Money market    | High (daily)              | 5-6%/yr         | 1-2%       | 1-6 months      |
| Reksa Dana Pendapatan Tetap | Fixed income    | Medium                    | 7-9%/yr         | 4-6%       | 1-3 years       |
| Reksa Dana Equity           | Equity          | High (daily)              | 12-15%/yr       | 18-22%     | 3-5 years       |
| REITs (DIRE)                | Real estate     | Medium                    | 10-12%/yr       | 12-16%     | 3-5 years       |

## Allocation Rules by Risk Profile

### Konservatif (Score 12-30)

- deposito: 30%, obligasi_ori_sbr: 40%, reksa_dana_pasar_uang: 15%,
  reksa_dana_pendapatan_tetap: 10%, reksa_dana_equity: 5%, reits: 0%
- Rationale: Capital preservation, income generation, minimal equity exposure

### Moderat (Score 31-45)

- deposito: 15%, obligasi_ori_sbr: 25%, reksa_dana_pasar_uang: 10%,
  reksa_dana_pendapatan_tetap: 20%, reksa_dana_equity: 22%, reits: 8%
- Rationale: Balance of income and growth, moderate volatility tolerance

### Agresif (Score 46-60)

- deposito: 0%, obligasi_ori_sbr: 5%, reksa_dana_pasar_uang: 0%,
  reksa_dana_pendapatan_tetap: 5%, reksa_dana_equity: 65%, reits: 25%
- Rationale: Long-term growth, high volatility tolerance, liquidity secondary

## Timeline Override Rules

**Critical**: Timeline overwrites risk profile for short horizons.

```
IF timeline_years < 3:
    cap equity at 40%
    cap reits at 10%
    DISPLAY WARNING: "With a timeline under 3 years, aggressive equity
    allocation is risky. We have capped your equity exposure at 40%."
ELIF timeline_years < 5:
    cap equity at 60%
    cap reits at 15%
    DISPLAY NOTICE: "Short timeline detected. Equity allocation reduced
    from {profile_recommendation}% to {adjusted}%."
```

## Portfolio Output Format

For each instrument:

```
instrument: string
percentage: float (0-100, must sum to 100)
monthly_amount_idr: float
expected_return_annual: float
volatility_annual: float
liquidity_tier: enum [high, medium, low]
```

## Projected Growth Trajectory

For each year from 0 to timeline_years:

```
year: int
starting_balance: float
contributions: float (monthly × 12)
investment_gains: float
ending_balance: float
```

Blended return rate = weighted average of all instrument expected returns.

## Shortfall Calculation

```
projected_value_at_goal_year: float
goal_amount: float
shortfall = goal_amount - projected_value_at_goal_year

IF shortfall > 0:
    DISPLAY: "Projected shortfall of Rp {shortfall:,.0f}"
    RECOMMEND: "Consider increasing monthly contribution by Rp {delta:,.0f}
    or extending your timeline by {years_extended} years"
ELSE:
    DISPLAY: "On track — projected surplus of Rp {surplus:,.0f}"
```

## Blended Return Formula

```
blended_return = Σ (allocation_percentage_i × expected_return_i)
blended_volatility = Σ (allocation_percentage_i × volatility_i)
  [Note: simplified; ignores correlation matrix for MVP]
```

## Competitor Comparison Test (Value Auditor Finding)

Before treating portfolio optimization as a differentiator, run this test:

```
Input: Risk profile = Moderat, timeline = 5 years
Input: Risk profile = Moderat, timeline = 20 years
Expected output if differentiated:
  5-year portfolio: higher bonds, lower equity
  20-year portfolio: higher equity, lower bonds

IF portfolios are structurally identical across timelines:
    DIFFERENTIATION CLAIM FAILS
    Vestara = Bibit with goal-themed onboarding
```

This test must pass for Vestara's portfolio differentiation claim to be credible.
