# C1: Hard Gate — Block Scenario Optimizer When Ratio >100%

## Problem

`scenario-optimizer.py` currently recommends "increase monthly contribution" even when a user's disposable income is zero or negative. The contribution lever is structurally impossible in this case — presenting it wastes user trust and makes the system look broken.

## Spec

Implements: `specs/scenario-optimizer.md` § "Required: Hard Gate"

## Changes

### `vestara/src/engine/scenario_optimizer.py`

1. Add a `validate_prerequisites()` function at the top of `run_scenario_analysis()`:
   - Compute `ratio = monthly_investment_required / disposable_income`
   - If `disposable_income <= 0`: return a special `ScenarioResult` with `recommended=None`, `current_verdict="red"`, and a `blocked_reason` field explaining the goal requires more than disposable income
   - If `ratio >= 1.0`: return with `blocked_reason="Contribution increase is not available — your required monthly investment exceeds your entire disposable income. Please consider reducing your goal size or exploring a lower-cost city."`
2. Add `blocked_reason: Optional[str]` field to `ScenarioResult` dataclass

### `vestara/src/ui/app.py` (Feasibility page)

1. After computing feasibility result, check `result.get("blocked_reason")` from scenario optimizer
2. If blocked, display a warning box: "⚠️ Your goal requires more than your disposable income. [blocked_reason]"

## Test

Add `tests/unit/test_scenario_optimizer.py`:

- `test_run_scenario_analysis_blocks_when_disposable_is_zero()`: disposable=0, assert `blocked_reason` is set
- `test_run_scenario_analysis_blocks_when_ratio_above_100pct()`: ratio=1.2, assert `blocked_reason` is set
- `test_run_scenario_analysis_proceeds_when_ratio_below_100pct()`: ratio=0.8, assert `blocked_reason` is None
- `test_run_scenario_analysis_proceeds_when_ratio_is_green()`: ratio=0.2, assert scenarios returned

## Constraints

- Do not change the scenario optimizer's normal return type for non-blocked cases
- Blocked path should not raise an exception — return a typed result with `blocked_reason`
- UI should display blocked reason in a warning box, not a traceback
