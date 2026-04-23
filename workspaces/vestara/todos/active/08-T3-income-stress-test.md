# T3: Income Stress Test — Show Impact of -50% Income Shock

## Problem

The feasibility analysis uses a single income projection (linear growth at user's stated rate). For users in volatile industries (tech, consulting, oil & gas), a 40-50% income reduction mid-journey is realistic. The system does not currently show users how resilient their plan is to income shocks.

## Spec

Implements: `specs/feasibility.md` (income projection section) and `specs/failure-points.md` § "Income Projection Error"

## Changes

### `vestara/src/engine/income_stress_test.py` (new file)

```python
def run_stress_test(
    monthly_salary: float,
    monthly_contribution: float,
    goal_cost: float,
    timeline_years: int,
    income_growth_rate: float,
) -> dict:
    """
    Returns stress test results for three scenarios:
    - Base: linear growth at stated rate
    - Stress -30%: income drops 30% at year 3, recovers at +3%/yr
    - Stress -50%: income drops 50% at year 3, recovers at +2%/yr
    """
    scenarios = {}
    for label, shock_pct, recovery_rate in [
        ("base", 0.0, income_growth_rate),
        ("stress_30pct", 0.30, 0.03),
        ("stress_50pct", 0.50, 0.02),
    ]:
        months, balances = simulate_income_path(
            monthly_salary, monthly_contribution, goal_cost,
            timeline_years, income_growth_rate, shock_pct, recovery_rate
        )
        scenarios[label] = {
            "final_balance": balances[-1],
            "shortfall": max(0, goal_cost - balances[-1]),
            "months_to_goal": months,
            "goal_achieved": balances[-1] >= goal_cost,
        }
    return scenarios

def simulate_income_path(...):
    # Compound monthly with shock at month 36, then recovery
```

### `vestara/src/ui/app.py` (Feasibility page)

Add a collapsible "Income Stress Test" section below the main feasibility verdict:

- Header: "What if your income drops by 30-50%?"
- Three columns: Base / -30% Shock / -50% Shock
- For each: "Final balance: Rp X" | "Shortfall: Rp Y or Surplus" | "Goal achieved: ✅/❌"
- Warning if both stress scenarios show shortfall: "⚠️ Your plan is sensitive to income shocks. Consider building a cash buffer or choosing a more conservative goal."
- Show industries: "This scenario is most relevant for tech, consulting, and oil & gas workers who face income volatility."

## Tests

`tests/unit/test_income_stress_test.py`:

- `test_stress_50pct_reduces_final_balance()`: assert stress_50pct final_balance < base final_balance
- `test_stress_50pct_shortfall_is_positive()`: assert shortfall > 0 for expensive goals
- `test_base_scenario_matches_projection()`: base scenario close to linear projection
- `test_stress_test_returns_all_three_scenarios()`: assert all three keys present

## Constraints

- Stress test is for display only — does not change the feasibility verdict
- The shock timing (year 3) and recovery rates are assumptions — document them in the UI
