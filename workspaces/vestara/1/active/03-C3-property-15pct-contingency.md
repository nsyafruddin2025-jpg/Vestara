# C3: Add 15% Contingency Buffer to Property Goal Costs

## Problem

Property goal costs currently estimate only the purchase price. In reality, Indonesian property transactions carry ~10-12% additional costs (PBB, notary, BPHTB, legal fees) and prices can appreciate 15-30% during the investment horizon. The current estimate understates the true cost by 10-25%.

## Spec

Implements: `specs/cost-database.md` § "Contingency Buffer"

## Changes

### `vestara/src/engine/goal_builder.py`

Update `estimate_property_cost()`:

```python
def estimate_property_cost(self, city: str, size_label: str) -> float:
    size_map = {
        "Studio / 1BR (24-36 sqm)": 30,
        "2BR Standard (45-54 sqm)": 50,
        "2BR Large / 3BR (70-90 sqm)": 80,
        "Large / Penthouse (90-150 sqm)": 120,
    }
    sqm = size_map.get(size_label, 54)
    price_per_sqm = PROPERTY_PRICE_PER_SQM.get(city, PROPERTY_PRICE_PER_SQM["Jakarta Selatan"])
    base_cost = sqm * price_per_sqm
    contingency_buffer = 1.15  # 15% for transaction costs + price appreciation
    return base_cost * contingency_buffer
```

### `vestara/src/engine/goal_builder.py` — Property volatility warning

After calculating property cost, if the city is in the high-volatility tier, add a warning:

- Cities: Jakarta Selatan, Surabaya CBD
- Warning message: "Property prices in {city} have shown 20-40% appreciation in 3-year windows. Your estimate may need updating as you approach your goal date."

### `vestara/src/ui/app.py` (Goal Builder — Property flow)

- Display line-item breakdown: "Base cost: Rp X" + "Contingency buffer (15%): Rp Y" + "Estimated total: Rp Z"
- If high-volatility city: show info box with volatility warning
- Display the `volatility_tier` in the goal profile summary

### Update `vestara/data/cost_data.py`

Add `PROPERTY_VOLATILITY_TIER` dict:

```python
PROPERTY_VOLATILITY_TIER = {
    "Jakarta Selatan": "high",
    "Surabaya CBD": "high",
    "Bandung": "medium",
    "Jakarta Pusat": "medium",
    "Bali (Denpasar)": "medium",
    "Medan": "low",
    "Semarang": "low",
    "Makassar": "low",
    "Yogyakarta": "low",
}
```

## Tests

`tests/unit/test_goal_builder.py`:

- `test_property_cost_includes_15pct_contingency()`: for a known city/size, assert estimated_cost == expected_base × 1.15
- `test_property_cost_correct_for_all_cities()`: loop all cities, verify contingency applied
- `test_property_volatility_tier_returned()`: assert high-volatility city returns volatility_tier in profile

## Constraints

- The contingency buffer must be shown explicitly to the user in the UI — not hidden
- Do not change cost estimates for other goal types
