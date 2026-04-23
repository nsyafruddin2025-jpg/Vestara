# C4: Cap Equity at 40% for Timelines Under 3 Years + Warning

## Problem

The portfolio optimizer currently recommends equity-heavy allocations (up to 65% for Agresif profile) regardless of goal timeline. For goals under 3 years, this exposes users to significant short-term volatility risk without time to recover. Indonesian investors who need money in 2 years cannot afford a 30% market downturn.

## Spec

Implements: `specs/portfolio-optimizer.md` § "Timeline Override Rules"

## Changes

### `vestara/src/portfolio/optimizer.py`

Update `build_portfolio()`:

```python
def build_portfolio(
    risk_profile: str,
    monthly_contribution: float,
    goal_amount: float,
    timeline_years: int,
) -> PortfolioProjection:
    # Apply timeline caps FIRST, before base allocation
    if timeline_years < 3:
        # Cap equity at 40%, reits at 10%
        adjusted_timeline = True
        warning = ("With a timeline under 3 years, aggressive equity allocation "
                   "is risky. We have capped your equity exposure at 40%.")
    elif timeline_years < 5:
        # Cap equity at 60%, reits at 15%
        adjusted_timeline = True
        warning = ("Short timeline detected. Equity allocation reduced from "
                   "{profile_pct}% to 60%.")
    else:
        adjusted_timeline = False
        warning = None

    # Then apply base risk-profile allocation, adjusting equity/reits if capped
    ...
```

Update `PortfolioProjection` dataclass to add:

```python
timeline_warning: Optional[str]
equity_cap_applied: bool
```

### `vestara/src/ui/app.py` (Portfolio Recommendation page)

1. After building portfolio, check `result.timeline_warning`
2. If `timeline_warning` is not None, display a warning/info box with the message
3. In the allocation table, annotate equity and REIT rows with "(capped)" if cap was applied

### `vestara/src/ui/app.py` (Feasibility page — scenario analysis)

When displaying scenario analysis, add a note: "If your timeline is under 3 years, equity-heavy portfolios carry significant short-term risk. Consider conservative instruments for the portion you'll need within 3 years."

## Tests

`tests/unit/test_portfolio_optimizer.py`:

- `test_equity_capped_at_40pct_for_timeline_2yr()`: timeline=2, assert reksa_dana_equity ≤ 40
- `test_equity_capped_at_60pct_for_timeline_4yr()`: timeline=4, assert reksa_dana_equity ≤ 60
- `test_no_cap_for_timeline_10yr()`: timeline=10, assert full equity allocation from profile applies
- `test_timeline_warning_returned_for_short_timeline()`: assert timeline_warning is not None for timeline=2
- `test_timeline_warning_none_for_long_timeline()`: assert timeline_warning is None for timeline=10

## Constraints

- The timeline cap must override the risk profile allocation, not supplement it
- Warning message must be specific to the user's timeline, not generic
- Do not apply caps to bonds, deposito, or pasar uang (these are not equity)
