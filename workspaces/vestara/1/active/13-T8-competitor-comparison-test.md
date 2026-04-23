# T8: Competitor Comparison Test — Portfolio Differentiation Validation

## Problem

Value auditor finding: Vestara's portfolio differentiation claim (goal-first vs product-first) is only valid if portfolios differ for users with the same risk profile but different timelines. If the portfolio for a 5-year Moderat user looks identical to a 20-year Moderat user, Vestara is just Bibit with a goal-themed onboarding.

## Spec

Implements: `specs/portfolio-optimizer.md` § "Competitor Comparison Test"

## Changes

### `vestara/tests/integration/test_portfolio_differentiation.py`

```python
def test_portfolios_differ_by_timeline():
    """Verify that portfolio changes significantly across timelines for same risk profile."""
    from vestara.src.portfolio.optimizer import build_portfolio

    moderat_5yr = build_portfolio("Moderat", monthly_contribution=2_000_000,
                                   goal_amount=500_000_000, timeline_years=5)
    moderat_20yr = build_portfolio("Moderat", monthly_contribution=2_000_000,
                                    goal_amount=500_000_000, timeline_years=20)

    # Extract equity percentage for both
    equity_5yr = next(a.percentage for a in moderat_5yr.allocations if a.instrument == "reksa_dana_equity")
    equity_20yr = next(a.percentage for a in moderat_20yr.allocations if a.instrument == "reksa_dana_equity")

    # 5-year should have less equity than 20-year
    assert equity_5yr < equity_20yr, (
        f"Portfolio differentiation claim FAILS: 5-year portfolio has "
        f"{equity_5yr}% equity vs 20-year has {equity_20yr}%. "
        f"They should differ."
    )

def test_short_timeline_triggers_cap():
    """Verify that <3 year timelines always cap equity at 40%."""
    ...

def test_agresif_20yr_has_max_equity():
    """Verify that long timeline + Agresif profile uses maximum equity allocation."""
    ...
```

### Add to `vestara/src/ui/app.py` — Competitor comparison display

On Portfolio page, add a collapsible "How is Vestara different?" section:

```
Vestara vs. Other Apps:
✅ We adjust your portfolio based on your goal timeline — not just your risk tolerance.
   A 5-year Moderat investor gets a more conservative portfolio than a 20-year Moderat investor.
❌ Most apps (Bibit, Bareksa) give the same portfolio to both users.

[Chart comparing Vestara 5yr vs 20yr vs Bibit-style fixed allocation]
```

Run the `test_portfolios_differ_by_timeline` test and display the result on the page.

## Tests

- `test_portfolios_differ_by_timeline()`: as defined above
- `test_all_profiles_have_timeline_sensitivity()`: loop all profiles, assert timeline changes allocation

## Constraints

- Test must be in the integration test suite
- Display of differentiation must be factual, not marketing copy
- If test fails, the differentiation claim must be acknowledged as unproven
