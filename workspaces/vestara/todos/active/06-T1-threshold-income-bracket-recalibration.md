# T1: Threshold Recalibration — Income Bracket and Goal-Type Aware

## Problem

All users currently get the same Green/Yellow/Red thresholds (30%/50%) regardless of income level, city, or goal type. A Rp 5M/month user and a Rp 25M/month user face the same boundaries, but their financial realities are completely different. Bank Indonesia data shows young urban professionals in Jakarta save 8-18%, not 30%.

## Spec

Implements: `specs/threshold-calibration.md` § "Required Calibration (Before Production)"

## Changes

### `vestara/src/engine/threshold_calibrator.py` (new file)

Create a `ThresholdCalibrator` class:

```python
class ThresholdCalibrator:
    INCOME_BRACKETS = {
        (0, 10_000_000): {"green": 0.25, "yellow": 0.50},   # Rp 5-10M
        (10_000_000, 20_000_000): {"green": 0.30, "yellow": 0.50},  # Rp 10-20M
        (20_000_000, 35_000_000): {"green": 0.35, "yellow": 0.55},  # Rp 20-35M
    }

    GOAL_TYPE_ADJUSTMENTS = {
        "Emergency Fund": {"green_delta": +0.10, "yellow_delta": +0.10},
        "Retirement": {"green_delta": -0.05, "yellow_delta": -0.05},
        "Education": {"green_delta": -0.05, "yellow_delta": -0.05},
        "Wedding": {"green_delta": -0.10, "yellow_delta": -0.05},
        "Property": {"green_delta": 0.00, "yellow_delta": 0.00},
        "Higher Education": {"green_delta": -0.05, "yellow_delta": -0.05},
        "Custom": {"green_delta": 0.00, "yellow_delta": 0.00},
    }

    def get_thresholds(self, monthly_salary: float, goal_type: str) -> tuple[float, float]:
        """Returns (green_boundary, yellow_boundary) calibrated to user profile."""
        bracket = self._get_income_bracket(monthly_salary)
        base_green, base_yellow = self.INCOME_BRACKETS[bracket]
        adjustments = self.GOAL_TYPE_ADJUSTMENTS.get(goal_type, {"green_delta": 0, "yellow_delta": 0})
        calibrated_green = base_green + adjustments["green_delta"]
        calibrated_yellow = base_yellow + adjustments["yellow_delta"]
        return calibrated_green, calibrated_yellow

    def _get_income_bracket(self, salary: float) -> tuple:
        for bracket, _ in sorted(self.INCOME_BRACKETS.items(), key=lambda x: x[0][0]):
            if bracket[0] <= salary < bracket[1]:
                return bracket
        return (20_000_000, 35_000_000)  # default to highest bracket
```

### Update `vestara/src/engine/feasibility_classifier.py`

Update the `FeasibilityClassifier` to accept an optional `ThresholdCalibrator`:

```python
def predict(self, X: pd.DataFrame, thresholds: Optional[ThresholdCalibrator] = None) -> np.ndarray:
    ...
    # Use calibrated thresholds if provided, else defaults
```

### Update `vestara/src/ui/app.py`

- Add a "Threshold Mode" toggle in Feasibility Analysis: "Default (30%/50%)" vs "Income-calibrated (recommended)"
- When income-calibrated mode is on, show which bracket and goal-type adjustments were applied
- Display: "Using income-calibrated thresholds: Green < {X}%, Yellow {X}-{Y}%, Red >{Y}%"
- In Default mode: show the disclaimer "Default thresholds are based on general household saving research. Income-calibrated mode uses bracket-specific research."

### Sensitivity Analysis Display

Add a sensitivity analysis panel (collapsible) showing:

- "If Green boundary shifts ±3pp, your verdict would: [change / stay same]"
- "If Yellow boundary shifts ±3pp, your verdict would: [change / stay same]"

## Tests

`tests/unit/test_threshold_calibrator.py`:

- `test_low_income_has_tighter_green_threshold()`: bracket 5-10M, assert green < 0.30
- `test_high_income_has_tighter_green_threshold()`: bracket 20-35M, assert green > 0.30
- `test_emergency_fund_has_looser_thresholds()`: assert green for Emergency Fund > green for Property
- `test_calibrator_returns_tuple()`: get_thresholds returns (float, float)
- `test_unknown_goal_type_uses_defaults()`: unknown goal type, assert no adjustment

## Constraints

- Default (non-calibrated) thresholds must remain available as a mode toggle
- Calibration must be transparent — user must see which bracket and goal-type adjustments were applied
- The sensitivity analysis must be in the UI, not just in tests
