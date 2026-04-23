# T4: Portfolio Growth Chart — Visual Trajectory Display

## Problem

The portfolio page currently shows only a text table of yearly balances. Users find it hard to intuitively understand whether they're on track. A simple line chart showing the portfolio growth curve vs the goal line would make the shortfall/surplus immediately obvious.

## Spec

Implements: `specs/portfolio-optimizer.md` § "Projected Growth Trajectory"

## Changes

### `vestara/src/ui/app.py` (Portfolio Recommendation page)

Replace the text-based trajectory table with a Streamlit chart:

```python
import streamlit as st

# Build chart data
goal_df = pd.DataFrame({
    "Year": [y for y, _ in result.yearly_trajectory],
    "Portfolio Value": [v for _, v in result.yearly_trajectory],
})
goal_df["Goal Line"] = result.goal_amount

# Line chart
st.line_chart(
    goal_df.set_index("Year"),
    height=400,
)
st.caption(
    f"Green line: portfolio value. "
    f"Red line: goal of Rp {result.goal_amount:,.0f}. "
    f"Projected value at year {result.timeline_years}: "
    f"Rp {result.projected_value_at_goal_year:,.0f}."
)
```

If `result.projected_value_at_goal_year < result.goal_amount`:

- Shade the area between the two lines in red (shortfall area)
- Add annotation: "Shortfall: Rp {shortfall:,.0f}"

### Also keep the text table below the chart as a fallback

## Tests

`tests/unit/test_portfolio_optimizer.py`:

- `test_yearly_trajectory_has_correct_length()`: assert len(trajectory) == timeline_years + 1
- `test_growth_trajectory_increases_over_time()`: assert each year >= previous year (monotonically increasing)
- `test_projected_value_at_goal_year_matches_trajectory_end()`: assert last trajectory value matches field

## Constraints

- Chart must be responsive and render correctly in Streamlit
- Keep text table as secondary display for accessibility
- If projected value exceeds goal, chart should show the surplus clearly
