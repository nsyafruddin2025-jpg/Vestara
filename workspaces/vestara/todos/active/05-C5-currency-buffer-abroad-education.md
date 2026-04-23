# C5: Currency Buffer for Abroad Higher Education Goals

## Problem

Higher education goals for overseas study are calculated in nominal IDR but denominated in foreign currency (AUD, EUR, USD, SGD). Over a 4-year degree program, IDR typically depreciates 3-5% per year against these currencies. Without a currency buffer, the system systematically underestimates abroad education costs by 12-20% in IDR terms.

## Spec

Implements: `specs/cost-database.md` § "Currency Buffer for Abroad Education"

## Changes

### `vestara/src/engine/goal_builder.py`

Update `estimate_higher_education_cost()`:

```python
def estimate_higher_education_cost(self, country: str, tier: str, degree: str) -> float:
    # ... existing base cost calculation ...

    # Currency depreciation buffer (3-5% per year compounded)
    annual_depreciation_rate = 0.04  # Conservative 4% IDR/year
    currency_years = degree_years  # 2, 4, or 5 years
    depreciation_factor = (1 + annual_depreciation_rate) ** currency_years

    # 10% contingency buffer on top
    total_buffer = depreciation_factor * 1.10

    return mid * years * multiplier * total_buffer
```

Add to `GoalProfile.to_dict()`:

```python
currency_buffer_applied: bool
currency_buffer_factor: float  # e.g. 1.17 for 4-year degree
```

### `vestara/src/ui/app.py` (Goal Builder — Higher Education flow)

Display the currency buffer as a separate line:

- "Base cost (IDR): Rp X"
- "Currency depreciation buffer (4%/yr × Y years): Rp Z"
- "Contingency (10%): Rp W"
- "Estimated total: Rp Total"
- Info box: "Costs for overseas education are shown in IDR. The currency buffer accounts for potential IDR depreciation over the study period — actual costs may be higher or lower depending on exchange rate movements."

### `vestara/src/engine/goal_builder.py` — Country-specific depreciation rates

```python
COUNTRY_DEPRECIATION_RATES = {
    "Australia": 0.04,   # IDR/AUD historical ~3-4%
    "Europe": 0.04,      # IDR/EUR historical ~3-4%
    "Singapore": 0.02,   # IDR/SGD more stable
    "US": 0.05,          # IDR/USD more volatile
    "Other": 0.04,
}
```

Apply per-country rate instead of flat 4%.

## Tests

`tests/unit/test_goal_builder.py`:

- `test_higher_ed_cost_includes_currency_buffer()`: assert estimated_cost > base_cost × years × multiplier
- `test_currency_buffer_factor_returned_in_profile()`: assert currency_buffer_applied == True
- `test_buffer_increases_with_degree_years()`: 4-year degree buffer > 2-year degree buffer
- `test_different_countries_have_different_rates()`: US rate > Singapore rate

## Constraints

- Buffer must be shown transparently in the UI — not hidden in the total
- Use country-specific depreciation rates, not a flat rate
- Buffer applies only to abroad education; domestic education does not need it
