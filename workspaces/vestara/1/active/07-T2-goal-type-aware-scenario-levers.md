# T2: Goal-Type-Aware Scenario Levers — Wedding and Education

## Problem

The scenario optimizer currently treats all goal types identically — recommending timeline extension as lever #1 for every Yellow/Red verdict. For Wedding and Education goals, timeline extension is not a real option: university admission dates and wedding seasons are fixed. The optimizer will propose impossible changes.

## Spec

Implements: `specs/scenario-optimizer.md` § "Goal-Type-Aware Lever Weights"

## Changes

### `vestara/src/engine/scenario_optimizer.py`

Update `run_scenario_analysis()` to accept `goal_type` parameter and apply goal-type-specific lever logic:

```python
LEVER_PRIORITY_BY_GOAL = {
    "Property": ["contribution", "goal_size", "timeline", "location"],
    "Education": ["contribution", "goal_size", "scholarship", "timeline"],
    "Retirement": ["timeline", "contribution", "goal_size", "lifestyle"],
    "Emergency Fund": ["contribution", "reduce_scope", "timeline"],
    "Wedding": ["goal_size", "contribution", "timeline"],
    "Higher Education": ["contribution", "scholarship", "goal_size", "timeline"],
    "Custom": ["goal_size", "contribution", "timeline", "location"],
}

FIXED_DEADLINE_GOALS = {"Wedding", "Education", "Higher Education"}

def run_scenario_analysis(
    goal_cost: float,
    monthly_salary: float,
    monthly_living_cost: float,
    current_timeline: int,
    current_contribution: float,
    goal_type: str = "Custom",
) -> ScenarioResult:
```

For `FIXED_DEADLINE_GOALS`, the `timeline` lever must include a warning flag:

```python
timeline_scenario.adjustment = f"Extend from {current_timeline} to {new_years} years"
timeline_scenario.change_description += (
    " WARNING: This goal has a natural deadline. "
    "Delaying may have social or academic consequences."
)
timeline_scenario.confidence = "LOW"  # deadline may not be truly flexible
```

### Add `scholarship` and `lifestyle` levers

```python
def optimize_scholarship(goal_cost, ...) -> Scenario:
    # Find scholarship alternatives that reduce net cost
    # e.g., "Bidik Misi", "Pertamina scholarship", "Australia Awards"
    # Show: "Scholarships could reduce cost by Rp X"
    ...

def optimize_lifestyle(goal_cost, ...) -> Scenario:
    # For retirement: suggest moving from "Premium" to "Comfortable" lifestyle
    # Show: "Reducing retirement lifestyle from Premium to Comfortable saves Rp X"
    ...
```

### `vestara/src/ui/app.py` (Feasibility page — Scenario Analysis)

- Display goal type in the scenario section header
- For Fixed-deadline goals: show a warning banner at top of scenario section: "⚠️ [Goal type] goals have natural deadlines — timeline extension may not be feasible in your situation."
- Show lever priority order as bullet list: "Our recommended adjustments (in priority order): [1] contribution, [2] goal_size, ..."
- For timeline lever on fixed-deadline goals: show with a ⚠️ prefix and LOW confidence badge

## Tests

`tests/unit/test_scenario_optimizer.py`:

- `test_wedding_removes_timeline_as_first_lever()`: assert lever order does not start with "timeline"
- `test_education_removes_timeline_as_first_lever()`: same for Education
- `test_property_timeline_is_available()`: assert "timeline" is in Property lever list
- `test_fixed_deadline_timeline_adder_warning()`: for Wedding, assert timeline scenario has confidence="LOW"
- `test_scenario_result_includes_goal_type()`: goal_type appears in output

## Constraints

- Do not remove the timeline lever for fixed-deadline goals — just de-prioritize it and add a warning
- The scholarship lever only applies to Education and Higher Education
- The lifestyle lever only applies to Retirement
